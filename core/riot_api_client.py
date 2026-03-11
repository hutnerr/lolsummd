import json
import requests

from typing import Optional
from util.cache.cache_interface import CacheInterface
from util.time_helper import *
from util.cache.redis_cache import RedisCache
from pyutils import Clogger, CloggerOverrideFactory
from pyutils import check_response
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
        self.masteryCacheDuration = TimeUnit.DAY1

        Clogger.info("RiotAPIClient initialized")

    def get_account_by_puuid(self, puuid: str) -> Optional[Account]:
        Clogger.warn("get_account_by_puuid is not implemented yet")
        pass

    def get_account_by_summoner_name(self, username: str, tag: str, region: Region) -> Optional[Account]:
        cached_data = self.cache.get_by_name(username, tag, region)
        if cached_data:
            Clogger.debug(f"Cache hit for account: {username}#{tag}")
            cached_data['region'] = Region(cached_data['region'])
            return Account(
                puuid=cached_data["puuid"],
                username=cached_data["username"],
                tag=cached_data["tag"],
                region=cached_data["region"]
            )

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
            self.cache.set(data["puuid"], {**account.__dict__, "region": region.value})
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

    def _get_cached_mastery(self, puuid: str) -> Optional[dict]:
        if not self.cache.has(puuid):
            return None
        
        cached_data = self.cache.get(puuid)
        mastery_cache = (cached_data or {}).get("masterydata", {})

        if not mastery_cache.get("cached_at"):
            return None
        if not is_cache_valid(mastery_cache["cached_at"], self.masteryCacheDuration):
            return None

        return mastery_cache.get("champions") or None


    def get_mastery_all_champions(self, account: Account) -> dict[int, dict[str, int]]:
        if not account or not account.puuid:
            Clogger.error("Invalid account provided for mastery fetch")
            return {}

        cached = self._get_cached_mastery(account.puuid)
        if cached:
            Clogger.debug(f"Cache hit for mastery: {account.username}#{account.tag}")
            return cached

        url = build_regional_url(account.region, ApiPath.MASTERY_BY_PUUID, puuid=account.puuid)
        params = {
            "api_key": self.key,
        }

        Clogger.debug(f"Fetching mastery data from API for {account.username}#{account.tag} at URL: {url}")
        # Clogger.debug(f"API params: {params}")

        try:
            response = requests.get(url, params=params, timeout=5)
            if not check_response(response):
                Clogger.warn(f"Failed to fetch mastery data for {account.username}#{account.tag}")
                return {}

            champions = {
                str(item["championId"]): {
                    "id":          item.get("championId"),
                    "level":       item.get("championLevel"),
                    "points":      item.get("championPoints"),
                    "last_played": item.get("lastPlayTime"),
                }
                for item in response.json()
                if "championId" in item
            }

            cached_account = self.cache.get(account.puuid) or {}
            cached_account["masterydata"] = {"cached_at": get_linux_timestamp(), "champions": champions}
            Clogger.debug(f"About to write mastery cache. cached_account keys: {list(cached_account.keys())}, username: {cached_account.get('username')}")
            self.cache.set(account.puuid, cached_account)

            return champions

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
    
    def is_same_account(self, acc1: list[str], acc2: list[str]) -> bool:
        acc1_username, acc1_tag, acc1_region = acc1
        acc2_username, acc2_tag, acc2_region = acc2
        
        if acc1_region != acc2_region:
            return False
        
        if acc1_tag != acc2_tag:
            return False
        
        if acc1_username.lower() != acc2_username.lower():
            return False
        
        Clogger.warn("Duplicate account detected based on username, tag, and region")
        return True