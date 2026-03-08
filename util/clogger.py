import sys
import time
from colorama import Fore, Style, Back, init
from functools import wraps
import inspect
import os

init(autoreset=True) # this is for colorama

class Clogger:
    debugEnabled  = True
    disabled      = False
    useTimestamps = True
    simpleTimestamp = True
    showSource    = True
    force_flush   = True

    @staticmethod
    def _getTimestamp():
        """Get formatted timestamp."""
        if not Clogger.useTimestamps:
            return ""
        if Clogger.simpleTimestamp:
            ts = time.strftime('%H:%M:%S', time.localtime())
        else:
            ts = time.strftime('%Y-%m-%d %H:%M:%S EST', time.localtime())
        return f"{Back.BLACK}{Fore.GREEN}{ts}{Style.RESET_ALL} "

    @staticmethod
    def _getCaller() -> str:
        """Walk up the stack to find the first frame outside of Clogger."""
        frame = inspect.currentframe()
        while frame:
            filename = os.path.basename(frame.f_code.co_filename)
            if filename != "clogger.py":
                return f"{filename}:{frame.f_lineno}"
            frame = frame.f_back
        return "unknown"

    @staticmethod
    def _log(tag: str, msg: str, color: str = ""):
        if Clogger.disabled:
            return

        timestamp = Clogger._getTimestamp()

        if Clogger.showSource:
            caller = Clogger._getCaller()
            source = f" {Fore.WHITE}{Style.DIM}{caller}{Style.RESET_ALL} |"
        else:
            source = ""

        print(
            f"{timestamp}{color}{tag:<8}{Style.RESET_ALL} |{source} {msg}",
            flush=Clogger.force_flush
        )

    @staticmethod
    def log(tag: str, msg: str):
        """Log with custom tag."""
        Clogger._log(f"[{tag.upper()}]", msg, Fore.CYAN)

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


# disable colors automatically if not in a TTY
if not sys.stdout.isatty():
    Fore.GREEN = Fore.RED = Fore.CYAN = Fore.BLUE = Fore.MAGENTA = Fore.YELLOW = ""
    Back.BLACK = Back.RESET = Style.RESET_ALL = Style.DIM = ""
