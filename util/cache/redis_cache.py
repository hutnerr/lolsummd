import json
import os
import redis
from typing import Optional, Dict, Any
from util.cache.cache_interface import CacheInterface
from util.clogger import Clogger


class RedisCache(CacheInterface):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
        password: Optional[str] = None, ttl: Optional[int] = None, key_prefix: str = "cache:"):
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            Clogger.error("REDIS_URL ENV NOT SET!!")

        self._client = (
            redis.Redis.from_url(redis_url, decode_responses=True)
            if redis_url
            else redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
            )
        )
        self._ttl = ttl
        self._prefix = key_prefix

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _puuid_key(self, puuid: str) -> str:
        """Redis key for a puuid entry."""
        return f"{self._prefix}accounts:{puuid}"

    def _name_key(self, username: str, tag: str, region: str) -> str:
        """Redis key for a name-index entry. Region included to support
        accounts with identical username#tag across different regions.
        """
        return f"{self._prefix}name_index:{username}#{tag}#{region}"

    def _serialize(self, value: Dict[str, Any]) -> str:
        return json.dumps(value)

    def _deserialize(self, raw: str) -> Dict[str, Any]:
        return json.loads(raw)

    def _store(self, redis_key: str, value: str) -> None:
        """Write a raw serialized string to Redis with optional TTL."""
        if self._ttl is not None:
            self._client.setex(redis_key, self._ttl, value)
        else:
            self._client.set(redis_key, value)

    # ------------------------------------------------------------------
    # CacheInterface implementation
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve account data by puuid."""
        raw = self._client.get(self._puuid_key(key))
        return self._deserialize(raw) if raw is not None else None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store account data under puuid and auto-update the name index
        when 'username', 'tag', and 'region' fields are present in the value.
        """
        self._store(self._puuid_key(key), self._serialize(value))

        if "username" in value and "tag" in value and "region" in value:
            self._store(
                self._name_key(value["username"], value["tag"], str(value["region"])),
                key,  # name index stores the puuid as a plain string
            )
            Clogger.log("CACHE", f"Set cache for {value['username']}#{value['tag']}#{value['region']} (puuid: {key})")
        else:
            Clogger.warn(f"Set cache for puuid {key} without username/tag/region fields; name index not updated")

    def has(self, key: str) -> bool:
        """Return True if the puuid key exists in cache."""
        return bool(self._client.exists(self._puuid_key(key)))

    def get_by_name(self, username: str, tag: str, region: str) -> Optional[Dict[str, Any]]:
        """Retrieve account data by username, tag, and region via the name index."""
        puuid = self._client.get(self._name_key(username, tag, region))
        if puuid:
            return self.get(puuid)
        return None

    def set_by_name(self, username: str, tag: str, region: str, value: Dict[str, Any]) -> None:
        """Store value via set(), which handles the name index automatically."""
        if "username" not in value or "tag" not in value or "region" not in value:
            value = {**value, "username": username, "tag": tag, "region": region}
        puuid = value.get("puuid", f"{username}#{tag}#{region}")
        self.set(puuid, value)

    def delete(self, key: str) -> None:
        """Remove a puuid entry and clean up its name-index entry."""
        account = self.get(key)
        if account is None:
            Clogger.warn(f"No entry found for key: {key}")
            return

        if "username" in account and "tag" in account and "region" in account:
            self._client.delete(
                self._name_key(account["username"], account["tag"], str(account["region"]))
            )

        Clogger.log("CACHE", f"Deleting key: {key}")
        self._client.delete(self._puuid_key(key))

    def clear(self) -> None:
        """Delete all keys that share this instance's prefix."""
        pattern = f"{self._prefix}*"
        cursor = 0
        while True:
            cursor, keys = self._client.scan(cursor, match=pattern, count=100)
            if keys:
                self._client.delete(*keys)
            if cursor == 0:
                break