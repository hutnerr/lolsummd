import requests
from util.clogger import Clogger

def check_response(response: requests.Response) -> bool:
        Clogger.debug(response.text)
        if not isinstance(response, requests.Response):
            Clogger.error("Invalid response object")
            return False
        
        c = response.status_code
        if c == 200:
            return True
        elif c == 404:
            Clogger.warn("Resource not found (404)")
        elif c == 403:
            Clogger.error("Forbidden (403) - check your API key permissions")
        elif c == 429:
            Clogger.error("Rate limit exceeded (429) - slow down your requests")
        else:
            Clogger.error(f"Unexpected error: {c}")
        
        data = response.json() if response.content else {}
        if "status" in data and "message" in data["status"]:
            Clogger.warn(f"{data['status']['message']}")

        return False