from rabbit.logger import logger


def expo(
    headers: dict | None,
    delay: int = 300000,
    base: int = 2,
    factor: int = 1,
    max_delay: int | None = None,
) -> int:
    """Exponential delay strategy."""
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
    headers: dict | None,
    delay: int = 300000,
    max_delay: int = 86400000,
) -> int:
    """Incremental delay strategy."""
    current_delay = _set_timeout(headers, delay)
    logger.debug(
        f"fibo delay strategy: [delay={delay}, current_delay={current_delay}, max_delay={max_delay}]"
    )
    if current_delay < max_delay:
        return int(current_delay + 60000)
    return int(max_delay)


def constant(headers: dict | None, delay: int = 300000) -> int:
    """Constant delay strategy."""
    logger.debug(f"constant delay strategy: [delay={delay}]")
    return delay


def _set_timeout(headers: dict | None, delay: int) -> int:
    if (headers is not None) and ("x-delay" in headers):
        delay = headers["x-delay"]
    return int(delay)
