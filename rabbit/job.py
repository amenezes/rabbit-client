import json

from rabbit import logger


async def async_echo_job(data: bytes) -> bytes:
    logger.warning("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    return bytes(json.dumps(data_response), "utf-8")
