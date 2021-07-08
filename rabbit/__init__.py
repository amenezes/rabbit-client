import logging

from .__version__ import __version__
from ._wait import constant, expo, fibo

logger = logging.getLogger("rabbit-client")
logger.addHandler(logging.NullHandler())

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exchange import Exchange
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.subscribe import Subscribe

__all__ = [
    "AioRabbitClient",
    "DLX",
    "Exchange",
    "Queue",
    "Publish",
    "Subscribe",
    "expo",
    "constant",
    "fibo",
]
