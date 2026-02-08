import os
from flask import Flask, render_template, request, session
from werkzeug.exceptions import HTTPException
from util.riot_api_client import RiotAPIClient
from util.clogger import Clogger
from core.mastery_summarizer import summarize_mastery

# setup
KEY_FILEPATH = os.path.join("data", "key.txt")
Clogger.debugEnabled = False

with open(KEY_FILEPATH, 'r') as f:
    key = f.read().strip()

try:
    client: RiotAPIClient = RiotAPIClient(key)
except Exception as e:
    Clogger.error(f"Failed to initialize RiotAPIClient: {e}")

app: Flask = Flask(__name__)
app.secret_key = os.urandom(24) # session management
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
                    Clogger.action(f"Added account: {username}#{tag}")
                else:
                    Clogger.warn(f"Account {username}#{tag} already added")
        
        elif action == "remove":
            remove_index = int(request.form.get("remove_index"))
            if 0 <= remove_index < len(session['accounts']):
                removed = session['accounts'].pop(remove_index)
                session.modified = True
                Clogger.action(f"Removed account: {removed[0]}#{removed[1]}")
        
        elif action == "clear":
            session['accounts'] = []
            session.modified = True
            Clogger.action("Cleared all accounts")
        
        elif action == "submit_all":
            accounts = session['accounts']
            
            if not accounts:
                Clogger.warn("No accounts to submit")
                return render_template("index.html", accounts=accounts)
            
            Clogger.debug("Accounts submitted:")
            for account in accounts:
                Clogger.action(f"ASKING FOR: {account[0]}#{account[1]}")
            
            riot_accounts = client.get_accounts_by_names(accounts)
            result = summarize_mastery(riot_accounts, client)
            
            return render_template("index.html", accounts=accounts, result=result)
    
    return render_template("index.html", accounts=session.get('accounts', []))

@app.route("/about")
def about():
    Clogger.action("About page requested")
    return render_template("about.html")

@app.route("/help")
def help():
    Clogger.action("Help page requested")
    return render_template("help.html")

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    Clogger.warn(f"HTTP Exception: {e.code} - {e.name}")
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
    Clogger.error(f"Internal Server Error: {e}")
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
    app.run(debug=True, port=5000)