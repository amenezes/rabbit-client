import asyncio
import logging
import os
import sys
from typing import Any, Tuple

import aioamqp
from aioamqp.channel import Channel
from aioamqp.protocol import AmqpProtocol

import attr

from rabbit.publish import Publish
from rabbit.subscribe import Subscribe


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitClient:

    _app = attr.ib(default=asyncio.get_event_loop())
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
    publish = attr.ib(
        type=Publish,
        default=Publish(),
        validator=attr.validators.instance_of(Publish)
    )
    subscribe = attr.ib(
        type=Subscribe,
        default=Subscribe(),
        validator=attr.validators.instance_of(Subscribe)
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

    @property
    def channel(self) -> Channel:
        return self._channel

    @property
    def protocol(self):
        return self._protocol

    async def connect(self, **kwargs) -> None:
        self._protocol = await self._get_protocol_connection(**kwargs)
        self._channel = await self._protocol.channel()
        await self._configure_pub_sub()

    async def _get_protocol_connection(self, **kwargs) -> AmqpProtocol:
        protocol = None
        try:
            *_, protocol = await aioamqp.connect(
                host=self.host,
                port=self.port,
                on_error=self.on_error_callback,
                **kwargs
            )
        except OSError:
            logging.info(f'Trying connect on {self.host}:{self.port}')
            await asyncio.sleep(30)
            await self.connect()

        return protocol

    async def on_error_callback(self, exception: Tuple[Any, Any]) -> None:
        """Reconnect on RabbitMQ callback."""
        logging.info(f'Application will be restarted on 30 seconds.')
        logging.error(f'Error: {exception}')
        await asyncio.sleep(10)
        sys.exit(1)

    async def _configure_pub_sub(self) -> None:
        self.publish.channel = self._channel
        self.subscribe.channel = self._channel

    async def configure(self) -> None:
        """Alias to configure subscribe and configure publish."""
        logging.info('Configuring the message broker...')
        await self.configure_subscribe()
        await self.configure_publish()
        logging.info('Message broker successfully configured.')

    async def configure_subscribe(self) -> None:
        await self.subscribe.configure()

    async def configure_publish(self) -> None:
        await self.publish.configure()
