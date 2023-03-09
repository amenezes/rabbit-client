import asyncio
import random
from typing import List, Optional
from uuid import uuid4

import aioamqp
from aioamqp.channel import Channel
from aioamqp.exceptions import AmqpClosedConnection
from aioamqp.protocol import AmqpProtocol
from attrs import field, mutable

from .background_tasks import BackgroundTasks
from .exceptions import AttributeNotInitialized
from .logger import logger


@mutable(repr=False)
class AioRabbitClient:
    transport = field(init=False, default=None)
    _protocol: AmqpProtocol = field(init=False, default=None)
    _event = field(factory=asyncio.Event)
    _background_tasks: BackgroundTasks = field(factory=BackgroundTasks)
    _items: List = field(factory=list)

    def __repr__(self) -> str:
        try:
            channels = len(self.protocol.channels)
        except AttributeError:
            channels = 0

        try:
            max_channels = self.protocol.server_channel_max
        except AttributeError:
            max_channels = 0

        try:
            connected = self.transport._protocol_connected
        except AttributeError:
            connected = False
        return f"AioRabbitClient(connected={connected}, channels={channels}, max_channels={max_channels}, background_tasks={self._background_tasks})"

    @property
    def server_properties(self) -> Optional[dict]:
        """Get server properties from the current connection."""
        try:
            return self.protocol.server_properties  # type: ignore
        except AttributeError:
            return None

    @property
    def protocol(self) -> AmqpProtocol:
        return self._protocol

    @protocol.setter
    def protocol(self, value: AmqpProtocol) -> None:
        self._protocol = value
        self._event.set()

    async def get_channel(self) -> Channel:
        """Get a new channel from current connection."""
        if not self.protocol:
            raise AttributeNotInitialized("Connection not initialized.")
        channel = await self.protocol.channel()
        return channel

    async def connect(self, **kwargs) -> None:
        """Connect to message broker."""
        self.transport, self.protocol = await aioamqp.connect(**kwargs)

    async def persistent_connect(self, **kwargs):
        """Connect to message broker ensuring reconnection in case of error."""
        while True:
            try:
                self.transport, self.protocol = await aioamqp.connect(**kwargs)
                await self.protocol.wait_closed()
                self.transport.close()
            except (OSError, aioamqp.exceptions.AmqpClosedConnection) as err:
                logger.error(
                    f"ConnectionError: [error='{err}', host='{kwargs.get('host')}', port={kwargs.get('port')}, login='{kwargs.get('login')}']"
                )
                await asyncio.sleep(5)
                await self.persistent_connect(**kwargs)

    async def register_watch(self, name: str, task, *args, **kwargs) -> None:
        self._background_tasks.add(name, task, *args, **kwargs)

    async def watch_connection_state(self, item) -> None:
        logger.debug("Watch connection enabled")
        self._event.clear()
        await self._event.wait()

        logger.error("Connection to RabbitMQ lost")
        logger.warning("Trying to establish a new connection...")
        item.channel = await self.get_channel()
        await item.configure()
        logger.warning("Connection restored")

    async def watch_channel_state(self, item) -> None:
        while True:
            await asyncio.sleep(5)
            logger.debug(f"Channel on '{item.name}' is open: {item.channel.is_open}")
            if not item.channel.is_open:
                try:
                    item.channel = await self.get_channel()
                    await item.configure()
                except AmqpClosedConnection:
                    pass

    async def register(self, item) -> None:
        await asyncio.sleep(random.uniform(1.0, 1.5))
        self._items.append(item)
        task_id = uuid4().hex
        item.channel = await self.get_channel()
        await item.configure()
        await self.register_watch(
            f"{item.name}-watch-connection-state-{task_id}",
            self.watch_connection_state,
            item,
        )
        await self.register_watch(
            f"{item.name}-watch-channel-state-{task_id}",
            self.watch_channel_state,
            item,
        )
