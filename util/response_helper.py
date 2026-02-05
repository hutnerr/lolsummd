import requests
from util.clogger import Clogger

def check_response(response: requests.Response) -> bool:
        Clogger.debug(response.text)
        if not isinstance(response, requests.Response):
            Clogger.error("Invalid response object")
            return False
        
        match response.status_code:
            case 200:
                return True
            case 404:
                Clogger.warn("Resource not found (404)")
            case 403:
                Clogger.error("Forbidden (403) - check your API key permissions")
            case 429:
                Clogger.error("Rate limit exceeded (429) - slow down your requests")
            case _:
                Clogger.error(f"Unexpected error: {response.status_code}")

        data = response.json() if response.content else {}
        if "status" in data and "message" in data["status"]:
            Clogger.warn(f"{data['status']['message']}")

        return False