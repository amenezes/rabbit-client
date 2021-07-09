import os
from typing import Optional


def expo(
    headers,
    initial_delay: int = int(os.getenv("EXPO_INITIAL_DELAY", 300000)),
    base: int = int(os.getenv("EXPO_BASE", 2)),
    factor: int = int(os.getenv("EXPO_FACTOR", 1)),
    max_delay: Optional[int] = os.getenv("EXPO_MAX_DELAY"),  # type: ignore
) -> int:
    time = base * factor
    if max_delay:
        max_delay = int(max_delay)
    current_delay = _set_timeout(headers, initial_delay)
    delay = int(current_delay * time)
    if max_delay is None or delay < max_delay:
        return delay
    return int(max_delay)


def fibo(
    headers,
    initial_delay: int = int(os.getenv("FIBO_INITIAL_DELAY", 300000)),
    max_delay: int = int(os.getenv("FIBO_MAX_DELAY", 86400000)),
) -> int:
    current_delay = _set_timeout(headers, initial_delay)
    if current_delay < max_delay:
        return int(current_delay + 60000)
    return int(max_delay)


def constant(
    headers, initial_delay: int = int(os.getenv("CONSTANT_DELAY", 300000))
) -> int:
    return _set_timeout(headers, initial_delay)


def _set_timeout(headers, delay: int) -> int:
    if (headers is not None) and ("x-delay" in headers):
        delay = headers["x-delay"]
    return int(delay)
