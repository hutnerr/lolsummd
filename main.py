import os
from pprint import pprint
from core.endpoint_builder import Region
from util.cache.redis_cache import RedisCache
from util.clogger import Clogger
from core.riot_api_client import RiotAPIClient
from core.mastery_summarizer import summarize_mastery
from core.ddragon_helper import get_champion_ids, get_champion_images
from util.env_loader import get_env

Clogger.debugEnabled = True

# get_champion_ids() # run this if you don't have data/champ_ids.json
# get_champion_images(true, true)  # run this if you don't have the icons and splashes

cache = RedisCache()
# cache.clear()

key = get_env("RIOT_API_KEY")
try:
    client = RiotAPIClient(key, cache=cache)
except Exception as e:
    Clogger.error(f"Failed to initialize RiotAPIClient: {e}")

account_info = [
    # ("username", "tag", Region.XXX)
    ("wizwizwizz", "1256", Region.NA1),
    ("the inescapable", "RAT", Region.EUW1),
    ("KC NEXT ADKING", "EUW", Region.EUW1),
    ("TFBlade", "122", Region.NA1),
    ("DK ShowMaker", "KR1", Region.KR)
]

accounts = client.get_accounts_by_names(account_info)
summarized_mastery = summarize_mastery(accounts, client)
pprint(summarized_mastery)
Clogger.info("End of main.py reached")
