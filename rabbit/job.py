import asyncio
import json
import random

from aio_pika.abc import AbstractIncomingMessage

from rabbit.logger import logger


async def async_echo_job(message: AbstractIncomingMessage) -> None:
    data = json.loads(message.body)
    logger.info(f"ECHO: {data}")


async def async_chaos_job(message: AbstractIncomingMessage) -> None:
    if random.choice([True, False]):
        await asyncio.sleep(30)
        raise Exception("Exception sample.")
    await async_echo_job(message)
