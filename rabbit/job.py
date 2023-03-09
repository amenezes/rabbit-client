import asyncio
import json
import random

from .logger import logger


async def async_echo_job(data: bytes, skip_wait: bool = True, *args, **kwargs) -> bytes:
    """async simple job."""
    logger.warning("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    if not skip_wait:
        logger.info("Waiting 30 seconds...")
        await asyncio.sleep(30)
    logger.info(f"ECHO: {data_response}")
    return bytes(json.dumps(data_response), "utf-8")


async def async_chaos_job(data: bytes, *args, **kwargs) -> bytes:
    """async chaos job."""
    if random.choice([True, False]):
        await asyncio.sleep(30)
        raise Exception("Exception sample.")
    data_response = await async_echo_job(data, True)
    return data_response
