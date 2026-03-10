import os
import json
import requests
from pyutils import check_response
from pyutils import Clogger

CHAMP_ID_FILEPATH = os.path.join("static", "champ_ids.json")
CHAMP_ICON_DIRPATH = os.path.join("static", "champion_icons")
CHAMP_SPLASH_DIRPATH = os.path.join("static", "champion_splashes")

def _get_latest_version() -> str:
    latest_version_response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if not check_response(latest_version_response):
        Clogger.error("Failed to fetch latest version from DDragon")
        return ""
    
    latest_version = latest_version_response.json()[0]
    return latest_version

# gets the champion ids from the saved file and not api
def get_champion_ids_saved() -> dict:
    if not os.path.exists(CHAMP_ID_FILEPATH):
        Clogger.error(f"Champion ID file not found at {CHAMP_ID_FILEPATH}")
        return {}

    with open(CHAMP_ID_FILEPATH, 'r') as f:
        raw = json.load(f)
        return {k: v["name"] for k, v in raw.items()}

# returns a dict mapping champion ID to champion name, and optionally saves it to a JSON file
def get_champion_ids(save: bool = True) -> dict:
    latest_version = _get_latest_version()
    if not latest_version:
        Clogger.error("Failed to fetch latest version from DDragon")
        return {}

    ddragon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    champions_response = requests.get(ddragon_url)
    if not check_response(champions_response):
        Clogger.error("Failed to fetch champion data from DDragon")
        return {}
    
    champions = champions_response.json()
    champions_data = champions.get("data", {})

    champ_id_to_name = {}
    for champion_key, champion_info in champions_data.items():
        champ_id = champion_info["key"]      # numeric ID, e.g. "200"
        champ_name = champion_info["name"]   # display name, e.g. "Bel'Veth"
        champ_file_key = champion_info["id"] # DDragon key, e.g. "Belveth"
        champ_id_to_name[champ_id] = {"name": champ_name, "file_key": champ_file_key}
    
    if save:
        with open(CHAMP_ID_FILEPATH, "w") as f:
            json.dump(champ_id_to_name, f, indent=4)
    
    return champ_id_to_name

def get_champion_icons_saved() -> dict:
    ids = get_champion_ids_saved()
    icons = {}
    for champ_id, champ_name in ids.items():
        filepath = os.path.join(CHAMP_ICON_DIRPATH, f"{champ_id}.png")
        if os.path.exists(filepath):
            icons[champ_id] = "/" + filepath
        else:
            Clogger.warn(f"Icon for champion ID {champ_id} not found in {CHAMP_ICON_DIRPATH}")
    return icons

def get_champion_images(getsplash: bool = True, geticon: bool = True):
    if not getsplash and not geticon:
        Clogger.warning("No images requested in get_champion_images()")
        return
    
    latest_version = _get_latest_version()
    if not latest_version:
        Clogger.error("Failed to fetch latest version from DDragon")
        return
    
    champ_id_to_name = get_champion_ids(save=True)
    
    os.makedirs(CHAMP_ICON_DIRPATH, exist_ok=True)
    os.makedirs(CHAMP_SPLASH_DIRPATH, exist_ok=True)

    for champ_id, champ_info in champ_id_to_name.items():
        champ_name = champ_info["name"]
        champ_file_key = champ_info["file_key"]
        icon_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/{champ_file_key}.png"
        splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_file_key}_0.jpg"
        
        if geticon:
            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                with open(os.path.join(CHAMP_ICON_DIRPATH, f"{champ_id}.png"), "wb") as f:
                    f.write(icon_response.content)
            else:
                Clogger.error(f"Failed to fetch icon for {champ_name} (ID: {champ_id}): {icon_response.status_code}")

        if getsplash:
            splash_response = requests.get(splash_url)
            if splash_response.status_code == 200:
                with open(os.path.join(CHAMP_SPLASH_DIRPATH, f"{champ_id}.jpg"), "wb") as f:
                    f.write(splash_response.content)
            else:
                Clogger.error(f"Failed to fetch splash for {champ_name} (ID: {champ_id}): {splash_response.status_code}")

    Clogger.info("Finished fetching champion images")