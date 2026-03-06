import json
import redis
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from util.cache.cache_interface import CacheInterface

class RedisCache(CacheInterface):
    """Redis-backed implementation of CacheInterface."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: Optional[int] = None,
        key_prefix: str = "cache:",
    ):
        """
        Args:
            host:       Redis server hostname.
            port:       Redis server port.
            db:         Redis database index.
            password:   Redis AUTH password (None for no auth).
            ttl:        Default time-to-live in seconds (None = no expiry).
            key_prefix: Namespace prefix applied to every key.
        """
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )
        self._ttl = ttl
        self._prefix = key_prefix

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def _name_key(self, username: str, tag: str) -> str:
        """Canonical key for username+tag look-ups."""
        return self._full_key(f"name:{username}:{tag}")

    def _serialize(self, value: Dict[str, Any]) -> str:
        return json.dumps(value)

    def _deserialize(self, raw: str) -> Dict[str, Any]:
        return json.loads(raw)

    def _store(self, redis_key: str, value: Dict[str, Any]) -> None:
        """Write to Redis with optional TTL."""
        serialized = self._serialize(value)
        if self._ttl is not None:
            self._client.setex(redis_key, self._ttl, serialized)
        else:
            self._client.set(redis_key, serialized)

    # ------------------------------------------------------------------
    # CacheInterface implementation
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from cache by key."""
        raw = self._client.get(self._full_key(key))
        return self._deserialize(raw) if raw is not None else None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store value in cache under key."""
        self._store(self._full_key(key), value)

    def has(self, key: str) -> bool:
        """Return True if key exists in cache."""
        return bool(self._client.exists(self._full_key(key)))

    def get_by_name(self, username: str, tag: str) -> Optional[Dict[str, Any]]:
        """Retrieve value by username and tag composite key."""
        raw = self._client.get(self._name_key(username, tag))
        return self._deserialize(raw) if raw is not None else None

    def set_by_name(self, username: str, tag: str, value: Dict[str, Any]) -> None:
        """Store value under a username+tag composite key."""
        self._store(self._name_key(username, tag), value)

    def delete(self, key: str) -> None:
        """Remove a key from the cache."""
        self._client.delete(self._full_key(key))

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