import os
from util.clogger import Clogger
from dotenv import load_dotenv

try:
    load_dotenv()
    Clogger.info("dotenv loaded successfully")
except ImportError:
    Clogger.warning("dotenv was not loaded")

def get_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        Clogger.error(f"ENV {name} NOT SET!!")
    return value