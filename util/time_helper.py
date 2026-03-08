from enum import Enum

class TimeUnit(Enum):
    NONE = 0
    MIN30 = 1800
    HOUR1 = 3600
    HOUR6 = 21600
    DAY1 = 86400

def get_linux_timestamp() -> int:
    import time
    return int(time.time())

def is_cache_valid(cached_time: int, time_unit: TimeUnit) -> bool:
    current_time = get_linux_timestamp()
    elapsed_time = current_time - cached_time
    return elapsed_time < time_unit.value
