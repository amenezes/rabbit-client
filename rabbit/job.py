import asyncio
import json
import random

from .logger import logger


async def async_echo_job(data: bytes) -> bytes:
    """async simple job."""
    await asyncio.sleep(random.randint(5, 10))
    logger.warning("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    logger.info(f"ECHO: {data_response}")
    return bytes(json.dumps(data_response), "utf-8")


async def async_chaos_job(data: bytes) -> bytes:
    """async chaos job."""
    if random.choice([True, False]):
        await asyncio.sleep(random.randint(5, 10))
        raise Exception("Exception sample.")
    data_response = await async_echo_job(data)
    return data_response
