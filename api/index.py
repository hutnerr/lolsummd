import os
import sys
from flask import Flask, render_template, request, session, jsonify
from werkzeug.exceptions import HTTPException
from core.riot_api_client import RiotAPIClient
from util.clogger import Clogger
from core.mastery_summarizer import summarize_mastery
from core.endpoint_builder import Region, REGION_TO_DEFAULT_TAG
from core.ddragon_helper import get_champion_icons_saved

Clogger.debugEnabled = True

key = os.environ.get("RIOT_API_KEY")
if not key:
    Clogger.error("ENV NOT SET: RiotAPIClient cannot be initialized without API key.")
    sys.exit(1)

client: RiotAPIClient = None
try:
    client = RiotAPIClient(key)
except Exception as e:
    Clogger.error(f"Failed to initialize RiotAPIClient: {e}")
    sys.exit(1)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)

flask_secret = os.environ.get("FLASK_SECRET_KEY")
if not flask_secret:
    Clogger.error("ENV NOT SET: FLASK_SECRET_KEY is not set. Sessions will not work.")
    sys.exit(1)
app.secret_key = flask_secret

Clogger.info("Flask app initialized")


def get_region_default_tags():
    return {r.value: tag for r, tag in REGION_TO_DEFAULT_TAG.items()}


# ── Page route ────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        accounts=session.get('accounts', []),
        regions=Region,
        region_default_tags=get_region_default_tags()
    )


# ── API: add account (validates against Riot API) ────────────────────────────

@app.route("/api/add", methods=["POST"])
def api_add():
    if 'accounts' not in session:
        session['accounts'] = []

    data = request.get_json()
    username = (data.get("username") or "").strip()
    tag      = (data.get("tag") or "").strip()
    region_str = (data.get("region") or "").strip()

    if not username or not tag or not region_str:
        return jsonify(error="Missing fields."), 400

    try:
        region = Region(region_str)
    except (ValueError, KeyError):
        return jsonify(error="Invalid region."), 400

    account = [username, tag, region.value]

    # Duplicate check
    if account in session['accounts']:
        return jsonify(error=f"{username}#{tag} is already in your list."), 409

    # Validate account exists via Riot API
    try:
        riot_accounts = client.get_accounts_by_names([(username, tag, region)])
        if not riot_accounts:
            return jsonify(error=f"Account {username}#{tag} was not found."), 404
    except Exception as e:
        Clogger.error(f"Riot API error during add: {e}")
        return jsonify(error=f"Account {username}#{tag} was not found."), 404

    if len(session['accounts']) >= 10:
        return jsonify(error="You can only add up to 10 accounts."), 400

    session['accounts'].append(account)
    session.modified = True

    Clogger.debug(f"Added account: {username}#{tag} ({region.value})")
    return jsonify(accounts=session['accounts'])


# ── API: remove account ───────────────────────────────────────────────────────

@app.route("/api/remove", methods=["POST"])
def api_remove():
    if 'accounts' not in session:
        return jsonify(accounts=[])

    data = request.get_json()
    try:
        idx = int(data.get("index"))
    except (TypeError, ValueError):
        return jsonify(error="Invalid index."), 400

    if 0 <= idx < len(session['accounts']):
        session['accounts'].pop(idx)
        session.modified = True

    return jsonify(accounts=session['accounts'])


# ── API: clear all accounts ───────────────────────────────────────────────────

@app.route("/api/clear", methods=["POST"])
def api_clear():
    session['accounts'] = []
    session.modified = True
    return jsonify(accounts=[])


# ── API: get combined mastery ─────────────────────────────────────────────────

@app.route("/api/submit", methods=["POST"])
def api_submit():
    accounts = session.get('accounts', [])
    if not accounts:
        return jsonify(error="No accounts added."), 400

    not_found = []
    valid_riot_accounts = []

    deserialized = [(a[0], a[1], Region(a[2])) for a in accounts]

    for username, tag, region in deserialized:
        try:
            found = client.get_accounts_by_names([(username, tag, region)])
            if found:
                valid_riot_accounts.extend(found)
            else:
                not_found.append(f"{username}#{tag}")
        except Exception as e:
            Clogger.error(f"Error fetching {username}#{tag}: {e}")
            not_found.append(f"{username}#{tag}")

    if not valid_riot_accounts:
        return jsonify(error="None of the accounts could be found.", not_found=not_found), 404

    result = summarize_mastery(valid_riot_accounts, client, True)
    Clogger.debug(result)

    # Serialize result to JSON-safe format
    result_list = [
        {
            "name":   champ_name,
            "id":     mastery_data.get("champion_id") or mastery_data.get("id") or "",
            "icon":   mastery_data.get("icon") or "",
            "level":  mastery_data.get("level", 0),
            "points": mastery_data.get("points", 0),
        }
        for champ_name, mastery_data in result
    ]

    return jsonify(result=result_list, not_found=not_found)


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return (
        render_template("error.html", code=e.code, name=e.name, description=e.description),
        e.code,
    )


@app.errorhandler(500)
def internal_server_error(e):
    return (
        render_template("error.html", code=500, name="Internal Server Error", description="Something went wrong on our end."),
        500,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)