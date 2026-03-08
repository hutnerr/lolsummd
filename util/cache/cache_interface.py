from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CacheInterface(ABC):

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve account data by puuid."""
        pass

    @abstractmethod
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store account data under puuid. Auto-indexes by name+region
        if 'username', 'tag', and 'region' are present in value.
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """Return True if the puuid key exists in cache."""
        pass

    @abstractmethod
    def get_by_name(self, username: str, tag: str, region: str) -> Optional[Dict[str, Any]]:
        """Retrieve account data by username, tag, and region."""
        pass

    @abstractmethod
    def set_by_name(self, username: str, tag: str, region: str, value: Dict[str, Any]) -> None:
        """Store account data keyed by username, tag, and region."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a puuid entry and its name-index entry."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all entries from the cache."""
        pass