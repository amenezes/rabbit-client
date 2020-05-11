import asyncio
import logging
import os
from typing import Dict

import aioamqp
import attr
from aioamqp.channel import Channel

from rabbit import AttributeNotInitialized
from rabbit.observer import Observer

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitClient:

    host = attr.ib(
        type=str,
        default=os.getenv("BROKER_HOST", "localhost"),
        validator=attr.validators.instance_of(str),
    )
    port = attr.ib(
        type=int,
        default=int(os.getenv("BROKER_PORT", 5672)),
        validator=attr.validators.instance_of(int),
    )
    username = attr.ib(
        type=str,
        default=os.getenv("BROKER_USERNAME", "guest"),
        validator=attr.validators.instance_of(str),
    )
    password = attr.ib(
        type=str,
        default=os.getenv("BROKER_PASSWORD", "guest"),
        validator=attr.validators.instance_of(str),
    )
    _observer = attr.ib(type=Observer, factory=Observer, init=False)
    _channel = attr.ib(init=False, default=None)
    protocol = attr.ib(init=False, default=None)
    transport = attr.ib(init=False, default=None)

    @property
    def channel(self) -> Channel:
        if not self._channel:
            raise AttributeNotInitialized("Do you need connect before.")
        return self._channel

    @channel.setter
    def channel(self, value) -> None:
        self._channel = value
        self._observer.notify()

    def watch(self, observer) -> None:
        logging.debug(
            f"Object {observer.__class__} " "registered to monitoring channel changes."
        )
        self._observer.attach(observer)

    async def connect(self, channel_max: int = 1, **kwargs) -> None:
        self.transport, self.protocol = await aioamqp.connect(
            host=self.host,
            port=self.port,
            login=self.username,
            password=self.password,
            channel_max=channel_max,
            **kwargs,
        )
        await self._configure_channel()

    async def _configure_channel(self) -> None:
        if self.protocol:
            await asyncio.sleep(5)
            self.channel = await self.protocol.channel()

    async def persistent_connect(
        self, channel_max: int = 1, **kwargs: Dict[str, str]
    ) -> None:
        while True:
            try:
                await asyncio.sleep(1)
                await self.connect(channel_max, **kwargs)
                await asyncio.sleep(2)
                await self.protocol.wait_closed()
                self.transport.close()
            except (OSError, aioamqp.exceptions.AmqpClosedConnection):
                logging.info(f"Trying connect on {self.host}:{self.port}")
                await asyncio.sleep(5)
                await self.persistent_connect()
