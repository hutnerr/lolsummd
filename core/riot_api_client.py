import json
import requests

from typing import Optional
from util.cache.cache_interface import CacheInterface
from util.cache.redis_cache import RedisCache
from util.clogger import Clogger
from util.response_helper import check_response
from models.account import Account
from core.endpoint_builder import Region, ApiPath, build_regional_url, build_platform_url_from_region
from core.ddragon_helper import get_champion_ids_saved, get_champion_icons_saved

class RiotAPIClient:

    @Clogger.log_errors
    def __init__(self, key: str, cache: CacheInterface = None):
        if not key:
            raise ValueError("API key must be provided")
        if not isinstance(key, str):
            raise TypeError("API key must be a string")
        if key.strip() == "":
            raise ValueError("API key cannot be empty or whitespace")
        if len(key) < 10:
            raise ValueError("API key is too short")

        self.key: str = key
        self.cache: CacheInterface = cache or RedisCache()
        self.championIDs: dict[str, str] = get_champion_ids_saved()
        self.championIDsToIcons: dict[str, str] = get_champion_icons_saved()

        Clogger.info("RiotAPIClient initialized")

    def get_account_by_puuid(self, puuid: str) -> Optional[Account]:
        Clogger.warn("get_account_by_puuid is not implemented yet")
        pass

    def get_account_by_summoner_name(self, username: str, tag: str, region: Region) -> Optional[Account]:
        cached_data = self.cache.get_by_name(username, tag, region)
        if cached_data:
            Clogger.debug(f"Cache hit for {username}#{tag}")
            cached_data['region'] = Region(cached_data['region'])
            return Account(**cached_data)

        try:
            url = build_platform_url_from_region(
                region,
                ApiPath.ACCOUNT_BY_ID,
                username=username,
                tag=tag
            )
            resp = requests.get(url, params={"api_key": self.key}, timeout=5)

            if not check_response(resp):
                return None

            data = resp.json()

            if "puuid" not in data:
                Clogger.warn(f"Account not found: {username}#{tag}")
                return None

            account = Account(puuid=data["puuid"], username=username, tag=tag, region=region)
            self.cache.set(data["puuid"], account.__dict__)
            return account

        except Exception as e:
            Clogger.error(f"Error fetching account by name: {e}")
            return None

    def get_accounts_by_names(self, names: list[tuple[str, str, Region]]) -> list[Account]:
        if not names:
            Clogger.error("No names provided to fetch accounts")
            return []

        if not isinstance(names, list):
            Clogger.error("Names parameter must be a list of tuples")
            return []

        for item in names:
            if not isinstance(item, tuple) or len(item) != 3:
                Clogger.error("Each item in names list must be a tuple of (username, tag, region)")
                return []

        accounts = []
        for name, tag, region in names:
            account = self.get_account_by_summoner_name(name, tag, region)
            if account:
                accounts.append(account)
            else:
                Clogger.warn(f"Account {name}#{tag} failed to fetch.")

        if not accounts:
            Clogger.error("No accounts were fetched.")

        return accounts

    def get_mastery_all_champions(self, account: Account) -> dict[int, dict[str, int]]:
        url = build_regional_url(
            account.region,
            ApiPath.MASTERY_BY_PUUID,
            puuid=account.puuid
        )

        try:
            response = requests.get(url, params={"api_key": self.key}, timeout=5)

            if not check_response(response):
                return {}

            data = {}
            for item in response.json():
                champ_id = item.get("championId")
                data[champ_id] = {
                    "id":          champ_id,
                    "level":       item.get("championLevel"),
                    "points":      item.get("championPoints"),
                    "last_played": item.get("lastPlayTime"),
                }
            return data

        except Exception as e:
            Clogger.error(f"Error fetching mastery data: {e}")
            return {}

    def get_champion_name_by_id(self, champ_id) -> Optional[str]:
        if champ_id is None:
            Clogger.error("Champion ID is None")
            return None

        cid = self.championIDs.get(str(champ_id))

        if cid is None:
            Clogger.warn(f"Champion ID {champ_id} not found in mapping")

        return cid
    
    def get_champion_icon_by_id(self, champ_id) -> Optional[str]:
        if champ_id is None:
            Clogger.error("Champion ID is None")
            return None

        icon_path = self.championIDsToIcons.get(str(champ_id))

        if icon_path is None:
            Clogger.warn(f"Champion icon for ID {champ_id} not found in mapping")

        return icon_path