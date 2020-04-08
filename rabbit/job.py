import json
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


def echo_job(data: bytes) -> bytes:
    logging.info("Using the standard callable to process subscribe events.")
    data_response = json.loads(data)
    return bytes(json.dumps(data_response), "utf-8")


async def async_echo_job(data: bytes) -> bytes:
    return echo_job(data)
