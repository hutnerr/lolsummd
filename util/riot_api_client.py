import enum
import requests
import json

from typing import Optional
from util.cache_interface import CacheInterface
from util.json_cache import JsonCache
from util.clogger import Clogger
from models.account import Account
from util.ddragon_helper import CHAMP_ID_FILEPATH
from util.response_helper import *

class Endpoints(enum.Enum):
    ACCOUNT_BY_ID = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
    MASTERY_BY_PUID = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"

# TODO: implement region handling properly
# likely going to have to implement a endpoint builder that takes region into account
class Region(enum.Enum):
    NA1 = "na1"
    EUW1 = "euw1"
    EUN1 = "eun1"
    KR = "kr"
    JP1 = "jp1"

class RiotAPIClient:

    @Clogger.log_errors
    def __init__(self, key: str, default_region: Region = Region.NA1, cache: CacheInterface = None):
        if not key:
            raise ValueError("API key must be provided")
        
        if not isinstance(key, str):
            raise TypeError("API key must be a string")
        
        if key.strip() == "":
            raise ValueError("API key cannot be empty or whitespace")
        
        if len(key) < 10:
            raise ValueError("API key is too short")    

        self.key: str = key
        self.default_region: Region = default_region
        self.cache: CacheInterface = cache or JsonCache()
        self.championIDs: dict[str, str] = {}

        with open(CHAMP_ID_FILEPATH, 'r') as f:
            self.championIDs = json.load(f)

        Clogger.info("RiotAPIClient initialized")
    
    def set_default_region(self, region: Region) -> bool:
        if not isinstance(region, Region):
            Clogger.error("Invalid region type, could not set default region")
            return False
        
        self.default_region = region
        Clogger.info(f"Default region set to {region.value}")
        return True
    
    def get_account_by_puuid(self, puuid: str) -> Optional[Account]:
        Clogger.warn("get_account_by_puuid is not implemented yet")
        pass
    
    def get_account_by_summoner_name(self, username: str, tag: str) -> Optional[Account]:
        cached_data = self.cache.get_by_name(username, tag)
        if cached_data:
            Clogger.debug(f"Cache hit for {username}#{tag}")
            return Account(**cached_data)
        
        try:
            url = f"{Endpoints.ACCOUNT_BY_ID.value}/{username}/{tag}?api_key={self.key}"
            resp = requests.get(url, timeout=5)

            if not check_response(resp):
                return None
            
            data = resp.json()

            if "puuid" not in data:
                Clogger.warn(f"Account not found: {username}#{tag}")
                return None
            
            account = Account(
                puuid=data["puuid"],
                username=username,
                tag=tag
            )
            
            self.cache.set(data["puuid"], account.__dict__)
            return account
            
        except Exception as e:
            Clogger.error(f"Error fetching account by name: {e}")
            return None

    def get_accounts_by_names(self, names: list[tuple[str, str]]) -> list[Account]:
        accounts = []

        if names is None or len(names) == 0:
            Clogger.error("No names provided to fetch accounts")
            return accounts
        
        if not isinstance(names, list):
            Clogger.error("Names parameter must be a list of tuples")
            return accounts
        
        for item in names:
            if not isinstance(item, tuple) or len(item) != 2:
                Clogger.error("Each item in names list must be a tuple of (username, tag)")
                return accounts

        for name, tag in names:
            account = self.get_account_by_summoner_name(name, tag)
            if account:
                accounts.append(account)
            else:
                Clogger.warn(f"Account {name}#{tag} failed to fetch.")
        
        if not accounts:
            Clogger.error("No accounts were fetched.")

        return accounts

    def get_mastery_all_champions(self, account: Account) -> dict[int, dict[str, int]]:
        url = f"{Endpoints.MASTERY_BY_PUID.value}/{account.puuid}?api_key={self.key}"

        try:
            response = requests.get(url, timeout=5)

            if not check_response(response):
                return {}
                
            data = {}
            for item in response.json():
                temp = {}
                temp["id"] = item.get("championId")
                temp["level"] = item.get("championLevel")
                temp["points"] = item.get("championPoints")
                temp["last_played"] = item.get("lastPlayTime")
                data[item.get("championId")] = temp

            return data
            
        except Exception as e:
            Clogger.error(f"Error fetching mastery data: {e}")
            return {}

    def get_champion_name_by_id(self, champ_id: int | str) -> Optional[str]:
        if champ_id is None:
            Clogger.error("Champion ID is None")
            return None
        
        cid = self.championIDs.get(str(champ_id))

        if cid is None:
            Clogger.warn(f"Champion ID {champ_id} not found in mapping")
        
        return cid