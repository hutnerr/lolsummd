from dataclasses import dataclass

@dataclass
class Account:
    puuid: str
    username: str
    tag: str

    def __str__(self):
        return f"{self.username}#{self.tag} ({self.puuid})"
