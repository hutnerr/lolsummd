import os
from pprint import pprint
from util.clogger import Clogger
from util.riot_api_client import RiotAPIClient
from core.mastery_summarizer import summarize_mastery
from util.ddragon_helper import get_champion_ids

# this file exists for testing and debugging purposes
# the flask website is ran through app.py

KEY_FILEPATH = os.path.join("data", "key.txt")
Clogger.debugEnabled = False

# get_champion_ids()  # run this if you don't have data/champ_ids.json

with open(KEY_FILEPATH, 'r') as f:
    key = f.read().strip()
    try:
        client = RiotAPIClient(key)
    except Exception as e:
        Clogger.error(f"Failed to initialize RiotAPIClient: {e}")

account_info = [
    # ("username", "tag")
]

accounts = client.get_accounts_by_names(account_info)
summarized_mastery = summarize_mastery(accounts, client)
pprint(summarized_mastery)
