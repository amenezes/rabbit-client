import asyncio
import logging
import os
from typing import Dict

import aioamqp
from aioamqp.channel import Channel

import attr

from rabbit.exceptions import AttributeNotInitialized
from rabbit.observer import Observer


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitClient:

    app = attr.ib(default=asyncio.get_event_loop())
    host = attr.ib(
        type=str,
        default=os.getenv('BROKER_HOST', 'localhost'),
        validator=attr.validators.instance_of(str)
    )
    port = attr.ib(
        type=int,
        default=int(os.getenv('BROKER_PORT', 5672)),
        validator=attr.validators.instance_of(int)
    )
    _observer = attr.ib(
        type=Observer,
        default=Observer(),
        init=False
    )
    _channel = attr.ib(init=False, default=None)
    _protocol = attr.ib(init=False, default=None)
    _transport = attr.ib(init=False, default=None)

    @property
    def channel(self) -> Channel:
        if not self._channel:
            raise AttributeNotInitialized(
                'Do you need connect before.'
            )
        return self._channel

    @channel.setter
    def channel(self, value) -> None:
        self._channel = value
        self._observer.notify(self.app)

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value) -> None:
        self._protocol = value

    @property
    def transport(self):
        return self._transport

    def monitor_connection(self, observer) -> None:
        logging.debug(f"Object {observer.__class__} registered to monitoring channel changes.")
        self._observer.attach(observer)

    async def connect(self, channel_max: int = 1, **kwargs) -> None:
        self._transport, self.protocol = await aioamqp.connect(
            host=self.host,
            port=self.port,
            channel_max=channel_max,
            **kwargs
        )
        await self._configure_channel()

    async def persistent_connect(self,
                                 channel_max: int = 1,
                                 **kwargs: Dict[str, str]) -> None:
        while True:
            try:
                await asyncio.sleep(5)
                await self.connect(channel_max, **kwargs)
                await asyncio.sleep(10)
                await self.protocol.wait_closed()
                self._transport.close()
            except OSError:
                logging.info(f'Trying connect on {self.host}:{self.port}')
                await asyncio.sleep(5)
                await self.persistent_connect()
            except aioamqp.exceptions.AmqpClosedConnection:
                logging.info(f'Trying connect on {self.host}:{self.port}')
                await asyncio.sleep(5)
                await self.persistent_connect()

    async def _configure_channel(self) -> None:
        if self.protocol:
            await asyncio.sleep(5)
            self.channel = await self.protocol.channel()
