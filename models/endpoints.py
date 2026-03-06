
import enum

class Endpoints(enum.Enum):
    ACCOUNT_BY_ID = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
    MASTERY_BY_PUID = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"
