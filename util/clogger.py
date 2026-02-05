import sys
import time
from colorama import Fore, Style, Back, init
from functools import wraps

init(autoreset=True) # initalize colorama

class Clogger:
    debugEnabled = True
    disabled = False
    useTimestamps = True
    
    @staticmethod
    def _getTimestamp():
        """Get formatted timestamp."""
        if Clogger.useTimestamps:
            return Back.BLACK + Fore.GREEN + time.strftime("%Y-%m-%d %H:%M:%S EST", time.localtime()) + Back.RESET + " "
        return ""
    
    @staticmethod
    def _log(tag: str, msg: str, color: str = ""):
        """Internal logging method."""
        if not Clogger.disabled:
            timestamp = Clogger._getTimestamp()
            print(f"{timestamp}{color}{tag:<8}{Style.RESET_ALL} | {msg}")
    
    @staticmethod
    def log(tag: str, msg: str):
        """Log with custom tag."""
        formattedTag = f"[{tag.upper()}]"
        Clogger._log(formattedTag, msg, Fore.CYAN)
    
    @staticmethod
    def error(msg: str):
        """Log error message."""
        Clogger._log("[ERROR]", msg, Fore.RED)
    
    @staticmethod
    def debug(msg: str):
        """Log debug message (only if debugEnabled)."""
        if Clogger.debugEnabled:
            Clogger._log("[DEBUG]", msg, Fore.MAGENTA)
    
    @staticmethod
    def action(msg: str):
        """Log action message."""
        Clogger._log("[ACTION]", msg, Fore.GREEN)
    
    @staticmethod
    def info(msg: str):
        """Log info message."""
        Clogger._log("[INFO]", msg, Fore.BLUE)

    @staticmethod
    def warn(msg: str):
        """Log warning message."""
        Clogger._log("[WARN]", msg, Fore.YELLOW)

    @staticmethod
    def log_errors(func):
        """Decorator that logs exceptions before re-raising them."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                Clogger.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper

# USAGE EXAMPLE
if __name__ == "__main__":
    Clogger.info("Initialized Clogger")
    Clogger.log("state", "Player changed state")
    Clogger.error("X went wrong")
    Clogger.debug("This is a debug message")
    Clogger.action("User clicked button")
    Clogger.warn("This is a warning message")