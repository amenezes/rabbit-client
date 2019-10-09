import asyncio
import logging
import os
from typing import Any, Callable, Dict, Tuple

import aioamqp
from aioamqp.channel import Channel
from aioamqp.exceptions import AmqpClosedConnection
from aioamqp.exceptions import ChannelClosed
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
    _protocol = attr.ib(
        default=None,
        init=False
    )
    _transport = attr.ib(
        default=None,
        init=False
    )
    _instances = attr.ib(
        type=list,
        default=[],
        init=False,
        validator=attr.validators.instance_of(list)
    )
    _auto_configure = attr.ib(repr=False, default=True)
    _channels = attr.ib(
        type=dict,
        default={},
        validator=attr.validators.instance_of(dict)
    )

    @property
    def instances(self):
        return self._instances

    @instances.setter
    def instances(self, value):
        if value not in self._instances:
            self._instances.append(value)

    @property
    def identity(self):
        return f"{id(self)}"

    @property
    def channel(self) -> Channel:
        _channel = self._channels.get(self.identity, {}).get(self.protocol_id)
        self._validate_property(_channel)
        return _channel

    @property
    def protocol(self) -> AmqpProtocol:
        self._validate_property(self._protocol)
        return self._protocol

    @property
    def protocol_id(self) -> str:
        return f"{id(self._protocol)}"

    @property
    def transport(self):
        self._validate_property(self._transport)
        return self._transport

    def _validate_property(self, prop: Callable) -> None:
        if not prop:
            raise AttributeNotInitialized(
                'Do you need call connect() before.'
            )

    async def connect(self, **kwargs: Dict[str, str]) -> None:
        logging.debug(self.identity)
        if self.identity not in self._channels.keys():
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
            self._channels.update({self.identity: {self.protocol_id: None}})
            await self._configure_channel()
            await asyncio.sleep(5)

    async def _configure_channel(self):
        for instance_id in self._channels.keys():
            for protocol_id, channel in self._channels.get(instance_id).items():
                logging.debug(f"CHANNEL: {channel}")
                try:
                    if not channel:
                        channel = await self._protocol.channel()
                    await channel.close()
                    if not channel.is_open:
                        await channel.open()
                        self._channels.update(
                            {instance_id: {protocol_id: channel}}
                        )
                except ChannelClosed:
                    pass
                except AmqpClosedConnection:
                    pass
        if self._auto_configure:
            self._auto_configure = False
            for instance in self.instances:
                await instance.configure()
                await asyncio.sleep(5)
        logging.debug(f"channels: {self._channels}")
        logging.debug(f"registered instances: {len(self.instances)}")

    async def _reconnect(self):
        await asyncio.sleep(30)
        self._channels = {}
        await self.connect()

    async def on_error_callback(self, exception: Tuple[Any, Any]) -> None:
        """Reconnect on RabbitMQ callback."""
        if not hasattr(exception, 'code'):
            self._auto_configure = True
            await self._reconnect()
