import asyncio

import aioamqp
import attr
from aioamqp.channel import Channel
from aioamqp.protocol import AmqpProtocol

from .exceptions import AttributeNotInitialized
from .logger import logger


@attr.s(slots=True, repr=False)
class AioRabbitClient:
    _protocol = attr.ib(type=AmqpProtocol, init=False, default=None)
    transport = attr.ib(init=False, default=None)
    _event = attr.ib(init=False)

    def __attrs_post_init__(self):
        self._event = asyncio.Event()

    async def watch(self, item):
        logger.info("Watch connection enabled.")
        self._event.clear()
        await self._event.wait()
        logger.error("Connection lost.")
        if not item.__module__.endswith(".dlx"):
            logger.warning("Trying to establish a new connection...")
            await item.configure()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        self._event.set()

    async def get_channel(self) -> Channel:
        if not self.protocol:
            raise AttributeNotInitialized("Connection not initialized.")
        channel = await self.protocol.channel()
        return channel

    async def connect(self, **kwargs) -> None:
        self.transport, self.protocol = await aioamqp.connect(**kwargs)

    async def persistent_connect(self, **kwargs):
        while True:
            try:
                self.transport, self.protocol = await aioamqp.connect(**kwargs)
                await asyncio.sleep(2)
                await self.protocol.wait_closed()
                self.transport.close()
            except (OSError, aioamqp.exceptions.AmqpClosedConnection) as err:
                logger.error(f"Error: {err} - Params: {kwargs}")
                await asyncio.sleep(5)
                await self.persistent_connect(**kwargs)
