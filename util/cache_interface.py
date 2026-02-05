from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class CacheInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store value in cache."""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def get_by_name(self, username: str, tag: str) -> Optional[Dict[str, Any]]:
        """Retrieve value by username and tag."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove key from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache."""
        pass