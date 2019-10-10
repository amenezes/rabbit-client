import asyncio
import logging
import os
from typing import Dict

import aioamqp
from aioamqp.channel import Channel

import attr

from rabbit.exceptions import AttributeNotInitialized


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
    _channel = attr.ib(init=False, default=None)
    _protocol = attr.ib(init=False, default=None)
    _transport = attr.ib(init=False, default=None)
    instances = attr.ib(
        type=list,
        default=[],
        validator=attr.validators.instance_of(list)
    )

    @property
    def channel(self) -> Channel:
        if not self._channel:
            raise AttributeNotInitialized(
                'Do you need connect before.'
            )
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    async def persistent_connect(self,
                                 channel_max=1,
                                 **kwargs: Dict[str, str]) -> None:
        while True:
            try:
                await asyncio.sleep(5)
                self._transport, self.protocol = await aioamqp.connect(
                    host=self.host,
                    port=self.port,
                    channel_max=1,
                    **kwargs
                )
                await self._configure_channel()
                await asyncio.sleep(10)
                for instance in self.instances:
                    await asyncio.sleep(5)
                    await instance.configure()
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

    async def simple_connect(self, channel_max=1, **kwargs) -> None:
        self._transport, self.protocol = await aioamqp.connect(
            host=self.host,
            port=self.port,
            channel_max=channel_max,
            **kwargs
        )
        await self._configure_channel()

    async def connect(self, channel_max=1, **kwargs) -> None:
        await self.simple_connect(channel_max, **kwargs)

    async def _configure_channel(self) -> None:
        if self.protocol:
            await asyncio.sleep(5)
            self._channel = await self.protocol.channel()
