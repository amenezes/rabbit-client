import asyncio
from typing import Optional

import aioamqp
from aioamqp.channel import Channel
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
        tasks_name = [t.get_name() for t in self._background_tasks]
        return f"AioRabbitClient(connected={connected}, channels={channels}, max_channels={max_channels}, background_tasks={tasks_name})"

    @property
    def server_properties(self) -> Optional[dict]:
        """Get server properties from the current connection."""
        try:
            return self.protocol.server_properties  # type: ignore
        except AttributeError:
            return None

    async def watch(self, item) -> None:
        logger.debug("Watch connection enabled")
        self._event.clear()
        await self._event.wait()
        logger.error("Connection lost")
        if not item.__module__.endswith(".dlx"):
            logger.warning("Trying to establish a new connection...")
            await item.configure()

    async def _watch_channel_state(self, item, *args, **kwargs) -> None:
        while True:
            await asyncio.sleep(5)
            if not item.channel.is_open:
                await item.channel.open()
                await item.configure(item.channel, *args, **kwargs)

    async def register_watch(self, name: str, task, *args, **kwargs) -> None:
        loop = asyncio.get_running_loop()
        task = loop.create_task(task(*args, **kwargs), name=name)
        self._background_tasks.add(name, task)
        task.add_done_callback(self._background_tasks.discard)

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
