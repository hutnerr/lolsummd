import os
import sys
import logging
from flask import Flask, render_template, request, session
from werkzeug.exceptions import HTTPException
from core.riot_api_client import RiotAPIClient
from pyutils import Clogger, CloggerSetting
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


# routes
@app.route("/", methods=["GET", "POST"])
def home():
    region_default_tags = {r.value: tag for r, tag in REGION_TO_DEFAULT_TAG.items()}

    if 'accounts' not in session:
        session['accounts'] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            username = request.form.get("username")
            tag = request.form.get("tag")
            region_str = request.form.get("region")

            try:
                region = Region(region_str)
            except (ValueError, KeyError):
                Clogger.error(f"Invalid region value received: {region_str}")
                return render_template("index.html", accounts=session.get('accounts', []), regions=Region, region_default_tags=region_default_tags, error="Invalid region selected.")

            Clogger.debug(f"Received form data - Username: {username}, Tag: {tag}, Region: {region}")
            Clogger.debug("Type of data received from form: typeof(username): {}, typeof(tag): {}, typeof(region): {}".format(
                type(username), type(tag), type(region)))

            if username and tag and region:
                account = [username, tag, region.value]
                if account not in session['accounts']:
                    session['accounts'].append(account)
                    session.modified = True
                else:
                    Clogger.warn(f"Account {username}#{tag} already added")

        elif action == "remove":
            try:
                remove_index = int(request.form.get("remove_index"))
            except (TypeError, ValueError):
                Clogger.error("Invalid remove_index received.")
                return render_template("index.html", accounts=session.get('accounts', []), regions=Region, region_default_tags=region_default_tags, error="Invalid remove index.")

            if 0 <= remove_index < len(session['accounts']):
                session['accounts'].pop(remove_index)
                session.modified = True

        elif action == "clear":
            session['accounts'] = []
            session.modified = True

        elif action == "submit_all":
            accounts = session['accounts']
            if not accounts:
                return render_template("index.html", accounts=accounts, regions=Region, region_default_tags=region_default_tags)

            deserialized_accounts = [(a[0], a[1], Region(a[2])) for a in accounts]
            riot_accounts = client.get_accounts_by_names(deserialized_accounts)
            result = summarize_mastery(riot_accounts, client, True)
            Clogger.debug(result, settings_override={CloggerSetting.PPRINT_ENABLED : True})

            return render_template("index.html", accounts=accounts, result=result, regions=Region, region_default_tags=region_default_tags)

    return render_template("index.html", accounts=session.get('accounts', []), regions=Region, region_default_tags=region_default_tags)


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

if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=True, port=5000)