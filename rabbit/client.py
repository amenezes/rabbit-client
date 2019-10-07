import asyncio
import logging
import os
from typing import Any, Callable, Dict, Tuple

import aioamqp
from aioamqp.channel import Channel
from aioamqp.protocol import AmqpProtocol

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
    _channel = attr.ib(
        type=Channel,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Channel)
        ),
        init=False
    )
    _protocol = attr.ib(
        default=None,
        init=False
    )
    _transport = attr.ib(
        default=None,
        init=False
    )
    instances = attr.ib(
        type=list,
        default=[],
        validator=attr.validators.instance_of(list)
    )
    _auto_configure = attr.ib(repr=False, default=False)
    _channels = attr.ib(repr=False, default={})

    @property
    def channel(self) -> Channel:
        self._validate_property(self._channel)
        return self._channel

    @property
    def protocol(self) -> AmqpProtocol:
        self._validate_property(self._channel)
        return self._protocol

    @property
    def transport(self):
        self._validate_property(self._channel)
        return self._transport

    def _validate_property(self, prop: Callable) -> None:
        if not prop:
            raise AttributeNotInitialized(
                'Do you need call connect() before.'
            )

    async def connect(self, **kwargs: Dict[str, str]) -> None:
        try:
            self._transport, self._protocol = await aioamqp.connect(
                host=self.host,
                port=self.port,
                on_error=self.on_error_callback,
                **kwargs
            )
        except OSError:
            logging.info(f'Trying connect on {self.host}:{self.port}')
            await self._reconnect()
        except aioamqp.exceptions.AmqpClosedConnection:
            logging.info(f'Trying connect on {self.host}:{self.port}')
            await self._reconnect()

        await self._configure_channel()

    async def _reconnect(self):
        await asyncio.sleep(30)
        self._channel = None
        await self.connect()

    async def _reconnect2(self):
        await asyncio.sleep(30)
        for channel_inst in self._channels.keys():
            self._channels.update({id(channel_inst): None})
        await self.connect()

    async def _configure_channel2(self):
        if len(self._channels) == 0:
            channel = await self._protocol.channel()
            self._channels.update({id(channel): channel})
        elif:
            for channel_inst in self._channels.keys():
                if not self._channels.get(channel_inst):
                    channel = await self._protocol.channel()
                    self._channels.update({channel_inst: channel})

        for channel_inst in self._channels.keys():
            for i in range(1 + 1, self._channels.get(channel_inst).channel_id + 1):
                await self._channels.get(channel_inst).close()

        for channel_inst in self._channels.keys():
            if not self._channels.get(channel_inst).is_open:
                await self._channels.get(channel_inst).open()

        for channel_inst in self._channels.keys():
            if (self._auto_configure) and (self._channels.get(channel_inst).channel_id == 1):
                self._auto_configure = False
                for instance in self.instances:
                    await instance.configure()
                    await asyncio.sleep(5)

    async def _configure_channel(self):
        if not self._channel:
            self._channel = await self._protocol.channel()

        for i in range(1 + 1, self._channel.channel_id + 1):
            await self._channel.close()

        if not self._channel.is_open:
            await self._channel.open()

        if (self._auto_configure) and (self._channel.channel_id == 1):
            self._auto_configure = False
            for instance in self.instances:
                await instance.configure()
                await asyncio.sleep(5)

    async def on_error_callback(self, exception: Tuple[Any, Any]) -> None:
        """Reconnect on RabbitMQ callback."""
        if not hasattr(exception, 'code'):
            self._auto_configure = True
            await self._reconnect()
