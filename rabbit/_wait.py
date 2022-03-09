import os
from typing import Optional

from .logger import logger


def expo(
    headers,
    delay: Optional[int] = None,
    base: Optional[int] = None,
    factor: Optional[int] = None,
    max_delay: Optional[int] = None,
) -> int:
    delay = delay or int(os.getenv("EXPO_DELAY", 300000))
    base = base or int(os.getenv("EXPO_BASE", 2))
    factor = factor = int(os.getenv("EXPO_FACTOR", 1))
    max_delay = max_delay or os.getenv("EXPO_MAX_DELAY")  # type: ignore
    if max_delay:
        max_delay = int(max_delay)

    current_delay = _set_timeout(headers, delay)
    updated_delay = int(current_delay * (base * factor))
    logger.debug(
        f"expo delay strategy: [delay={delay}, current_delay={current_delay}, base={base}, factor={factor}, max_delay={max_delay}]"
    )
    if max_delay is None or updated_delay <= max_delay:
        return updated_delay
    return max_delay


def fibo(
    headers,
    delay: Optional[int] = None,
    max_delay: Optional[int] = None,
) -> int:
    delay = delay or int(os.getenv("FIBO_DELAY", 300000))
    max_delay = max_delay or int(os.getenv("FIBO_MAX_DELAY", 86400000))

    current_delay = _set_timeout(headers, delay)
    logger.debug(
        f"fibo delay strategy: [delay={delay}, current_delay={current_delay}, max_delay={max_delay}]"
    )
    if current_delay < max_delay:
        return int(current_delay + 60000)
    return int(max_delay)


def constant(headers, delay: Optional[int] = None) -> int:
    delay = delay or int(os.getenv("CONSTANT_DELAY", 300000))
    logger.debug(f"constant delay strategy: [delay={delay}]")
    return delay


def _set_timeout(headers, delay: int) -> int:
    if (headers is not None) and ("x-delay" in headers):
        delay = headers["x-delay"]
    return int(delay)
