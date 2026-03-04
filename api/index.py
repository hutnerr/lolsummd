import os
from flask import Flask, render_template, request, session
from werkzeug.exceptions import HTTPException
from util.riot_api_client import RiotAPIClient
from util.clogger import Clogger
from core.mastery_summarizer import summarize_mastery

# setup
Clogger.debugEnabled = False

key = os.environ.get("RIOT_API_KEY")
if not key:
    Clogger.error("ENV NOT SET: RiotAPIClient cannot be initialized without API key.")

try:
    client: RiotAPIClient = RiotAPIClient(key)
except Exception as e:
    Clogger.error(f"Failed to initialize RiotAPIClient: {e}")

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../templates")
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

Clogger.info("Flask app initialized")

# routes
@app.route("/", methods=["GET", "POST"])
def home():
    if 'accounts' not in session:
        session['accounts'] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            username = request.form.get("username")
            tag = request.form.get("tag")

            if username and tag:
                account = (username, tag)
                if account not in session['accounts']:
                    session['accounts'].append(account)
                    session.modified = True
                else:
                    Clogger.warn(f"Account {username}#{tag} already added")

        elif action == "remove":
            remove_index = int(request.form.get("remove_index"))
            if 0 <= remove_index < len(session['accounts']):
                session['accounts'].pop(remove_index)
                session.modified = True

        elif action == "clear":
            session['accounts'] = []
            session.modified = True

        elif action == "submit_all":
            accounts = session['accounts']

            if not accounts:
                return render_template("index.html", accounts=accounts)

            riot_accounts = client.get_accounts_by_names(accounts)
            result = summarize_mastery(riot_accounts, client)

            return render_template("index.html", accounts=accounts, result=result)

    return render_template("index.html", accounts=session.get('accounts', []))


@app.route("/help")
def help():
    return render_template("help.html")


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