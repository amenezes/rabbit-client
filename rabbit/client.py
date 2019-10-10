import asyncio
import logging
import uuid
import os
from typing import Any, Callable, Dict, Tuple

import aioamqp
from aioamqp.channel import Channel
from aioamqp.exceptions import AmqpClosedConnection
from aioamqp.exceptions import ChannelClosed
from aioamqp.exceptions import SynchronizationError
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
    # _identity = attr.ib(default=uuid.uuid4().hex, init=False)
    identity = attr.ib(default=uuid.uuid4().hex)

    @property
    def instances(self):
        return self._instances

    @instances.setter
    def instances(self, value):
        if value not in self._instances:
            self._instances.append(value)

    # @property
    # def identity(self):
    #     return f"{id(self)}"

    # @property
    # def identity(self):
    #     return f"{self._identity}"

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

    def __attrs_post_init__(self):
        self._channels = {self.identity: {}}

    async def connect(self, **kwargs: Dict[str, str]) -> None:
        # if self.identity not in self._channels.keys():
        if not self._channels.get(self.identity).keys():
            try:
                logging.info(f"HAS protocol: {self._channels.get(self.identity).keys()}")
                _, proto = await aioamqp.connect(
                # self._transport, self._protocol = await aioamqp.connect(
                    host=self.host,
                    port=self.port,
                    on_error=self.on_error_callback,
                    channel_max=1,
                    **kwargs
                )
                self._channels.update({self.identity: {proto: None}})
            except OSError:
                logging.info(f'Trying connect on {self.host}:{self.port}')
                await self._reconnect()
            except aioamqp.exceptions.AmqpClosedConnection:
                logging.info(f'Trying connect on {self.host}:{self.port}')
                await self._reconnect()
            # self._channels.update({self.identity: {self.protocol_id: None}})
            for x in self._channels.get(self.identity, {}):
                await self._configure_channel2(x)
        else:
            logging.info(f"ELSE: {self._channels}")
            for proto in self._channels.get(self.identity).keys():
                logging.info(f"STATUS: {proto.state}")
                if proto.state != 1:
                    self._channels = {self.identity: {}}
                    await asyncio.sleep(5)
                    await self._reconnect()
                    # try:
                    #     await proto.ensure_open()
                    # except aioamqp.exceptions.AmqpClosedConnection:
                    #     logging.info(f'Trying connect on {self.host}:{self.port}')
                    #     await self._reconnect()

    async def _configure_channel2(self, proto):
        try:
            channel = await proto.channel()
            logging.info(f"CHANNELS: {proto.channels}")
            if int(channel.channel_id) != 1:
                await channel.close()
            logging.info(f'CHANNEL ID: {channel.channel_id} | {channel.is_open}')
            if not channel.is_open:
                await channel.open()
            self._channels.update({self.identity: {proto: channel}})
        except ChannelClosed:
            pass
        except AmqpClosedConnection:
            pass

        if self._auto_configure:
            self._auto_configure = False
            for instance in self.instances:
                await instance.configure()
        logging.debug(f"channels: {self._channels}")
        logging.debug(f"registered instances: {len(self.instances)}")

    # async def _configure_channel(self):
    #     for instance_id in self._channels.keys():
    #         for protocol_id, channel in self._channels.get(instance_id).items():
    #             try:
    #                 logging.info(f"---- instance_id: {instance_id} | protocol_id: {protocol_id} | channel: {channel} -----")
    #                 if not channel:
    #                     channel = await self._protocol.channel()
    #                 await channel.close()
    #                 if not channel.is_open:
    #                     await asyncio.sleep(5)
    #                     await channel.open()
    #                     self._channels.update(
    #                         {instance_id: {protocol_id: channel}}
    #                     )
    #             except ChannelClosed:
    #                 pass
    #             except AmqpClosedConnection:
    #                 pass
    #     if self._auto_configure:
    #         self._auto_configure = False
    #         for instance in self.instances:
    #             # await asyncio.sleep(5)
    #             await instance.configure()
    #     logging.debug(f"channels: {self._channels}")
    #     logging.debug(f"registered instances: {len(self.instances)}")

    async def _reconnect(self):
        await asyncio.sleep(10)
        # if self._channels.get(self.identity):
        #     for x in self._channels.get(self.identity):
        #         await x.wait_closed()
        # self._channels = {}
        # self._channels = {self.identity: {}}
        for proto in self._channels.get(self.identity):
            logging.info(proto.state)
            self._channels = {self.identity: {proto: None}}
        await self.connect()

    async def on_error_callback(self, exception: Tuple[Any, Any]) -> None:
        """Reconnect on RabbitMQ callback."""
        if not hasattr(exception, 'code'):
            self._auto_configure = True
            await self._reconnect()
