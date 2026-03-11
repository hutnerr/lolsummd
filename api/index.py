import os
import sys
import logging
from flask import Flask, render_template, request, session, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException
from pyutils import Clogger, CloggerSetting
from core.riot_api_client import RiotAPIClient
from core.mastery_summarizer import summarize_mastery
from core.endpoint_builder import Region, REGION_TO_DEFAULT_TAG, REGION_TO_NAME
from core.ddragon_helper import get_champion_icons_saved
from models.account import Account

# ===============
# INIT
# ===============

key = os.environ.get("RIOT_API_KEY")
if not key:
    Clogger.error("ENV NOT SET: RiotAPIClient cannot be initialized without API key.")

client: RiotAPIClient = None
try:
    client = RiotAPIClient(key)
except Exception as e:
    Clogger.error(
        f"Failed to initialize RiotAPIClient: {e}",
        exc=Exception
    )

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "../static")
)

flask_secret = os.environ.get("FLASK_SECRET_KEY")
if not flask_secret:
    Clogger.error(
        "ENV NOT SET: FLASK_SECRET_KEY is not set. Sessions will not work.",
        exc=Exception
    )
app.secret_key = flask_secret

Clogger.info("Flask app initialized")

# ===============
# Routes
# ===============


@app.route("/", methods=["GET"])
def home():
    region_default_tags = {r.value: tag for r, tag in REGION_TO_DEFAULT_TAG.items()}
    region_names = {r.value: name for r, name in REGION_TO_NAME.items()}

    if 'accounts' not in session:
        session['accounts'] = []

    return render_template(
        "index.html",
        accounts=session.get('accounts', []),
        regions=Region,
        region_default_tags=region_default_tags,
        region_names=region_names,
    )
    
@app.route("/riot.txt")
def riot_file():
    return send_from_directory(app.static_folder, "riot.txt", mimetype="text/plain")

@app.route("/accounts", methods=["POST"])
def manage_accounts():
    """Handles add / remove / clear via fetch — returns JSON."""
    if 'accounts' not in session:
        session['accounts'] = []

    action = request.form.get("action")

    if action == "add":
        username = request.form.get("username", "").strip()
        tag = request.form.get("tag", "").strip()
        region_str = request.form.get("region", "").strip()

        try:
            region = Region(region_str)
        except (ValueError, KeyError):
            Clogger.error(f"Invalid region value received: {region_str}")
            return jsonify({"error": "Invalid region selected."}), 400

        Clogger.debug(f"Add account — Username: {username}, Tag: {tag}, Region: {region}")

        if username and tag and region:
            account = [username, tag, region.value]
            if account not in session['accounts']:
                if len(session['accounts']) >= 10:
                    return jsonify({"error": "Maximum of 10 accounts allowed."}), 400
                
                a = client.get_account_by_summoner_name(username, tag, region)                
                if not a:
                    return jsonify({"error": f"Account {username}#{tag} not found in region {region.value}."}), 404
                
                for acc in session['accounts']:
                    if client.is_same_account(account, acc):
                        Clogger.warn(f"Account {username}#{tag} already added (duplicate check)")
                        return jsonify({"error": f"{username}#{tag} has already been added."}), 400
                
                session['accounts'].append(account)
                session.modified = True
                return jsonify({"accounts": session['accounts'], "message": f"{username}#{tag} added."})
            else:
                Clogger.warn(f"Account {username}#{tag} already added")
                return jsonify({"error": f"{username}#{tag} has already been added."}), 400
        else:
            return jsonify({"error": "Username, tag, and region are all required."}), 400

    elif action == "remove":
        try:
            remove_index = int(request.form.get("remove_index"))
        except (TypeError, ValueError):
            Clogger.error("Invalid remove_index received.")
            return jsonify({"error": "Invalid remove index."}), 400

        if 0 <= remove_index < len(session['accounts']):
            session['accounts'].pop(remove_index)
            session.modified = True
            return jsonify({"accounts": session['accounts'], "message": "Account removed."})
        else:
            return jsonify({"error": "Index out of range."}), 400

    elif action == "clear":
        session['accounts'] = []
        session.modified = True
        return jsonify({"accounts": [], "message": "All accounts cleared."})

    else:
        return jsonify({"error": "Unknown action."}), 400


@app.route("/mastery", methods=["POST"])
def get_mastery():
    if 'accounts' not in session or not session['accounts']:
        return jsonify({"error": "No accounts in session."}), 400

    accounts = session['accounts']
    Clogger.debug(f"Session accounts ({len(accounts)}): {accounts}")

    deserialized_accounts = [(a[0], a[1], Region(a[2])) for a in accounts]
    Clogger.debug(f"Deserialized ({len(deserialized_accounts)}): {deserialized_accounts}")

    try:
        riot_accounts = client.get_accounts_by_names(deserialized_accounts)
        Clogger.debug(f"Riot accounts returned ({len(riot_accounts)}): {[(a.username, a.tag) for a in riot_accounts]}")

        result = summarize_mastery(riot_accounts, client, True)
        # Clogger.debug(result, settings_override={CloggerSetting.PPRINT_ENABLED: True})
    except Exception as e:
        Clogger.error(f"Mastery lookup failed: {e}")
        return jsonify({"error": "Failed to retrieve mastery data. Please try again."}), 500
    
    # result is a list of (champ_name, mastery_data_dict) tuples
    serialized = [
        {
            "name": champ_name,
            "level": mastery_data["level"],
            "points": mastery_data["points"],
            "icon": mastery_data.get("icon", ""),
        }
        for champ_name, mastery_data in result
    ]

    return jsonify({"result": serialized, "message": "Mastery data retrieved successfully."})


# ===============
# Error Handlers
# ===============

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return (
        render_template(
            "error.html",
            code=e.code,
            name=e.name,
            description=e.description,
        ),
        e.code,
    )

@app.errorhandler(500)
def internal_server_error(e):
    return (
        render_template(
            "error.html",
            code=500,
            name="Internal Server Error",
            description="Something went wrong on our end.",
        ),
        500,
    )

# ===============
# Main
# ===============

if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=True, port=5000)