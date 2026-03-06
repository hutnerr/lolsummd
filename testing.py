import os
from pprint import pprint
from util.clogger import Clogger
from core.riot_api_client import RiotAPIClient
from core.mastery_summarizer import summarize_mastery
from core.ddragon_helper import get_champion_ids, get_champion_images

KEY_FILEPATH = os.path.join("data", "key.txt")
Clogger.debugEnabled = True

with open(KEY_FILEPATH, 'r') as f:
    key = f.read().strip()
    
try:
    client = RiotAPIClient(key)
except Exception as e:
    Clogger.error(f"Failed to initialize RiotAPIClient: {e}")

# 1. need to test getting data from other regions besides NA
# 2. need to get the images of champions 

out = get_champion_images()
print(out)