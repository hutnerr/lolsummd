import os
from pprint import pprint
from util.clogger import Clogger
from util.riot_api_client import RiotAPIClient
from core.mastery_summarizer import summarize_mastery

KEY_FILEPATH = os.path.join("data", "key.txt")

Clogger.debugEnabled = False

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
