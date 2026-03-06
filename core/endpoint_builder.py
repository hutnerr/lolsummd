from enum import Enum

class ApiPath(str, Enum):
    SUMMONER_BY_NAME       = "/lol/summoner/v4/summoners/by-name/{summonerName}"
    SUMMONER_BY_PUUID      = "/lol/summoner/v4/summoners/by-puuid/{puuid}"
    SUMMONER_BY_ID         = "/lol/summoner/v4/summoners/{summonerId}"
    SUMMONER_BY_ACCOUNT_ID = "/lol/summoner/v4/summoners/by-account/{accountId}"
    ACCOUNT_BY_ID          = "/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
    MASTERY_BY_PUUID       = "/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"

class Platform(str, Enum):
    AMERICAS = "americas"
    EUROPE   = "europe"
    ASIA     = "asia"
    SEA      = "sea"
    
class Region(str, Enum):
    NA1   = "na1"
    EUW1  = "euw1"
    EUNE1 = "eune1"
    KR    = "kr"
    JP1   = "jp1"
    BR1   = "br1"
    LA1   = "la1"
    LA2   = "la2"
    OC1   = "oc1"
    TR1   = "tr1"
    RU    = "ru"
    PH2   = "ph2"
    SG2   = "sg2"
    TH2   = "th2"
    TW2   = "tw2"
    VN2   = "vn2"

REGION_TO_PLATFORM: dict[Region, Platform] = {
    Region.NA1:   Platform.AMERICAS,
    Region.BR1:   Platform.AMERICAS,
    Region.LA1:   Platform.AMERICAS,
    Region.LA2:   Platform.AMERICAS,
    Region.EUW1:  Platform.EUROPE,
    Region.EUNE1: Platform.EUROPE,
    Region.TR1:   Platform.EUROPE,
    Region.RU:    Platform.EUROPE,
    Region.KR:    Platform.ASIA,
    Region.JP1:   Platform.ASIA,
    Region.OC1:   Platform.SEA,
    Region.PH2:   Platform.SEA,
    Region.SG2:   Platform.SEA,
    Region.TH2:   Platform.SEA,
    Region.TW2:   Platform.SEA,
    Region.VN2:   Platform.SEA,
}

BASE_URL = "https://{host}.api.riotgames.com"

# For endpoints tied to a single server: summoner, mastery, league, etc.
def build_regional_url(region: Region, api_path: ApiPath, **kwargs) -> str:
    path = api_path.value.format(**kwargs) if kwargs else api_path.value
    return f"{BASE_URL.format(host=region.value)}{path}"

# for continental endpoints: match history, account lookup, etc.
def build_platform_url(platform: Platform, api_path: ApiPath, **kwargs) -> str:
    path = api_path.value.format(**kwargs) if kwargs else api_path.value
    return f"{BASE_URL.format(host=platform.value)}{path}"

def build_platform_url_from_region(region: Region, api_path: ApiPath, **kwargs) -> str:
    return build_platform_url(REGION_TO_PLATFORM[region], api_path, **kwargs)