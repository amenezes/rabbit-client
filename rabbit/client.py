import asyncio
import random
from typing import List, Union
from uuid import uuid4

import aioamqp
from aioamqp.channel import Channel
from aioamqp.exceptions import (
    AmqpClosedConnection,
    ChannelClosed,
    NoChannelAvailable,
    SynchronizationError,
)
from aioamqp.protocol import AmqpProtocol
from attrs import field, mutable

from .background_tasks import BackgroundTasks
from .exceptions import AttributeNotInitialized, ClientNotConnectedError
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
    def server_properties(self) -> Union[None, dict]:
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

    async def persistent_connect(self, **kwargs) -> None:
        """Connect and stay connected with exponential backoff.

        Runs indefinitely — reconnects automatically on failure.
        Cancel this task to stop reconnecting.
        """
        delay_s = 1
        while True:
            try:
                self.transport, self.protocol = await aioamqp.connect(**kwargs)
                await self.protocol.wait_closed()
                self.transport.close()
                delay_s = 1
            except (OSError, AmqpClosedConnection) as err:
                logger.error(
                    f"ConnectionError: [error='{err}', host='{kwargs.get('host')}', port={kwargs.get('port')}, login='{kwargs.get('login')}']"
                )
                if self.transport:
                    self.transport.close()
                await asyncio.sleep(delay_s)
                delay_s = min(delay_s * 2, 300)

    async def register_watch(self, name: str, task, *args, **kwargs) -> None:
        self._background_tasks.add(name, task, *args, **kwargs)

    async def watch_connection_state(self, item) -> None:
        """Reconfigure item when connection is re-established."""
        while True:
            await self._event.wait()
            try:
                item.channel = await self.get_channel()
                await item.configure()
                self._event.clear()
            except (
                AmqpClosedConnection,
                OSError,
                ChannelClosed,
                SynchronizationError,
                NoChannelAvailable,
                AttributeNotInitialized,
                ClientNotConnectedError,
            ) as err:
                logger.warning(
                    f"Reconnection recovery failed for '{item.name}': {err}. "
                    "Retrying on next reconnection..."
                )
                await asyncio.sleep(1)
            except Exception:
                logger.error(
                    f"Unexpected error reconnecting '{item.name}'",
                    exc_info=True,
                )
                await asyncio.sleep(5)

    async def watch_channel_state(self, item) -> None:
        """Recover closed channels on the current connection."""
        failures = 0
        while True:
            await asyncio.sleep(5)
            try:
                if item.channel.is_open:
                    failures = 0
                    continue
            except (ClientNotConnectedError, AttributeError):
                await asyncio.sleep(1)
                continue

            try:
                item.channel = await self.get_channel()
                await item.configure()
                failures = 0
            except (
                AmqpClosedConnection,
                OSError,
                ChannelClosed,
                SynchronizationError,
                NoChannelAvailable,
                AttributeNotInitialized,
                ClientNotConnectedError,
            ) as err:
                failures += 1
                logger.warning(
                    f"Channel recovery failed for '{item.name}' "
                    f"({failures}x): {err}"
                )

    async def register(self, item) -> None:
        await asyncio.sleep(random.uniform(1.0, 1.5))
        task_id = uuid4().hex
        item.channel = await self.get_channel()
        await item.configure()
        self._items.append(item)
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
