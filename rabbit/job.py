import asyncio
import json
from random import randint

from rabbit import logger


async def async_echo_job(data: bytes) -> bytes:
    """Async job."""
    await asyncio.sleep(randint(1, 10))
    logger.warning("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    logger.info(f"ECHO: {data_response}")
    return bytes(json.dumps(data_response), "utf-8")


async def dlx_job(data: bytes) -> None:
    """DLX job"""
    await asyncio.sleep(randint(1, 10))
    logger.warning("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    logger.info(f"DLX job: {data_response}")
    raise Exception("DLX job test")
