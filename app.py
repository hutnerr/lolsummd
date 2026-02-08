import os
from flask import Flask, render_template, request
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
Clogger.info("Flask app initialized")

# routes
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        accounts = []
        for i in range(1, 6):
            username = request.form.get(f"username{i}")
            tag = request.form.get(f"tag{i}")

            if username and tag:
                accounts.append((username, tag))
    
        Clogger.debug("Accounts submitted:")
        for account in accounts:
            Clogger.action(f"ASKING FOR: {account[0]}#{account[1]}")

        riot_accounts = client.get_accounts_by_names(accounts)
        result = summarize_mastery(riot_accounts, client)
        
        return render_template("index.html", accounts=accounts, result=result)
    
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
