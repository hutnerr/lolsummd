from enum import Enum

class ApiPath(str, Enum):
    # SUMMONER_BY_NAME       = "/lol/summoner/v4/summoners/by-name/{summonerName}"
    # SUMMONER_BY_PUUID      = "/lol/summoner/v4/summoners/by-puuid/{puuid}"
    # SUMMONER_BY_ID         = "/lol/summoner/v4/summoners/{summonerId}"
    # SUMMONER_BY_ACCOUNT_ID = "/lol/summoner/v4/summoners/by-account/{accountId}"
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

REGION_TO_NAME: dict[Region, str] = {
    Region.NA1:   "North America",
    Region.BR1:   "Brazil",
    Region.LA1:   "Latin America North",
    Region.LA2:   "Latin America South",
    Region.EUW1:  "Europe West",
    Region.EUNE1: "Europe Nordic & East",
    Region.TR1:   "Turkey",
    Region.RU:    "Russia",
    Region.KR:    "Korea",
    Region.JP1:   "Japan",
    Region.OC1:   "Oceania",
    Region.PH2:   "Philippines",
    Region.SG2:   "Singapore",
    Region.TH2:   "Thailand",
    Region.TW2:   "Taiwan",
    Region.VN2:   "Vietnam",
}

# warning: these might be wrong lol
REGION_TO_DEFAULT_TAG = {
    Region.NA1:   "NA1",
    Region.BR1:   "BR1",
    Region.LA1:   "LA1",
    Region.LA2:   "LA2",
    Region.EUW1:  "EUW1",
    Region.EUNE1: "EUN1",
    Region.TR1:   "TR1",
    Region.RU:    "RU",
    Region.KR:    "KR",
    Region.JP1:   "JP1",
    Region.OC1:   "OC1",
    Region.PH2:   "PH2",
    Region.SG2:   "SG2",
    Region.TH2:   "TH2",
    Region.TW2:   "TW2",
    Region.VN2:   "VN2",
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