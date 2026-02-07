import os
import json
import requests
from util.response_helper import *

CHAMP_ID_FILEPATH = os.path.join("data", "champ_ids.json")

def get_champion_ids(save: bool = True) -> dict:
    latest_version_response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if not check_response(latest_version_response):
        Clogger.error("Failed to fetch latest version from DDragon")
        return {}
    
    latest_version = latest_version_response.json()[0]

    ddragon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    champions_response = requests.get(ddragon_url)
    if not check_response(champions_response):
        Clogger.error("Failed to fetch champion data from DDragon")
        return {}
    
    champions = champions_response.json()
    champions_data = champions.get("data", {})

    champ_id_to_name = {}
    for champion_key, champion_info in champions_data.items():
        champ_id = champion_info["key"]
        champ_name = champion_info["name"]
        champ_id_to_name[champ_id] = champ_name
    
    if save:
        with open("data/champ.json", "w") as f:
            json.dump(champ_id_to_name, f, indent=4)
    
    return champ_id_to_name