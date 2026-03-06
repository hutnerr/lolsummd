from dataclasses import dataclass
from core.endpoint_builder import Region

@dataclass
class Account:
    puuid: str
    username: str
    tag: str
    region: Region

    def __str__(self):
        return f"{self.username}#{self.tag} ({self.puuid})"
