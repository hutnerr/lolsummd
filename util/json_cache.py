import json
import os
from typing import Optional, Dict, Any
from util.cache_interface import CacheInterface
from util.clogger import Clogger

DEFAULT_FILEPATH = os.path.join("data", "cache.json")

class JsonCache(CacheInterface):
    def __init__(self, cache_file: str = DEFAULT_FILEPATH):
        self.cache_file = cache_file
        self._puuid_cache: Dict[str, Dict[str, Any]] = {}  # puuid -> account data
        self._name_to_puuid: Dict[str, str] = {}  # "username#tag" -> puuid
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._puuid_cache = data.get("accounts", {})
                    self._name_to_puuid = data.get("name_index", {})
                Clogger.info(f"Loaded {len(self._puuid_cache)} accounts from cache")
            except Exception as e:
                Clogger.error(f"Failed to load cache from disk: {e}")
                self._puuid_cache = {}
                self._name_to_puuid = {}
        else:
            Clogger.info("No existing cache file found, starting fresh")
    
    def _save_to_disk(self) -> None:
        try:
            data = {
                "accounts": self._puuid_cache,
                "name_index": self._name_to_puuid
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            Clogger.error(f"Failed to save cache to disk: {e}")
    
    def get(self, key: str) -> Dict[str, Any] | None:
        return self._puuid_cache.get(key)
    
    def get_by_name(self, username: str, tag: str) -> Dict[str, Any] | None:
        name_key = f"{username}#{tag}"
        puuid = self._name_to_puuid.get(name_key)
        if puuid:
            return self._puuid_cache.get(puuid)
        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._puuid_cache[key] = value
        
        # also update the name -> puuid index
        if "username" in value and "tag" in value:
            name_key = f"{value['username']}#{value['tag']}"
            self._name_to_puuid[name_key] = key
        
        self._save_to_disk()
    
    def has(self, key: str) -> bool:
        return key in self._puuid_cache
    
    def delete(self, key: str) -> None:
        if key not in self._puuid_cache:
            return 
    
        # also remove from name index
        account = self._puuid_cache[key]
        if "username" in account and "tag" in account:
            name_key = f"{account['username']}#{account['tag']}"
            self._name_to_puuid.pop(name_key, None)
        
        del self._puuid_cache[key]
        self._save_to_disk()
    
    def clear(self) -> None:
        self._puuid_cache = {}
        self._name_to_puuid = {}
        self._save_to_disk()