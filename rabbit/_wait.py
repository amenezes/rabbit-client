import os
from typing import Optional

from .logger import logger


def expo(
    headers,
    delay: int = int(os.getenv("EXPO_DELAY", 300000)),
    base: int = int(os.getenv("EXPO_BASE", 2)),
    factor: int = int(os.getenv("EXPO_FACTOR", 1)),
    max_delay: Optional[int] = os.getenv("EXPO_MAX_DELAY"),  # type: ignore
) -> int:
    logger.debug(
        f"expo delay strategy: [delay={delay}, base={base}, factor={factor}, max_delay={max_delay}]"
    )
    if max_delay:
        max_delay = int(max_delay)
    current_delay = _set_timeout(headers, delay)
    delay_updated = int(current_delay * (base * factor))
    if max_delay is None or delay_updated <= max_delay:
        return delay_updated
    return int(max_delay)


def fibo(
    headers,
    delay: int = int(os.getenv("FIBO_DELAY", 300000)),
    max_delay: int = int(os.getenv("FIBO_MAX_DELAY", 86400000)),
) -> int:
    logger.debug(f"fibo delay strategy: [delay={delay}, max_delay={max_delay}]")
    current_delay = _set_timeout(headers, delay)
    if current_delay < max_delay:
        return int(current_delay + 60000)
    return int(max_delay)


def constant(headers, delay: int = int(os.getenv("CONSTANT_DELAY", 300000))) -> int:
    logger.debug(f"constant delay strategy: [delay={delay}]")
    return _set_timeout(headers, delay)


def _set_timeout(headers, delay: int) -> int:
    if (headers is not None) and ("x-delay" in headers):
        delay = headers["x-delay"]
    return int(delay)
