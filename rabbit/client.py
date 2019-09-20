import asyncio
import logging
import os

import aioamqp
from aioamqp.channel import Channel

import attr

from rabbit.dlx import DLX
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
        default=os.getenv('BROKER_PORT', 5672),
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
    dlx = attr.ib(
        type=DLX,
        default=DLX(),
        validator=attr.validators.instance_of(DLX)
    )
    _channel = attr.ib(
        type=Channel,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Channel)
        ),
        init=False
    )

    @property
    def channel(self):
        return self._channel

    async def connect(self):
        protocol = await self._get_protocol_connection()
        self._channel = await protocol.channel()
        await self._configure_pub_sub()

    async def _get_protocol_connection(self):
        protocol = None
        try:
            *_, protocol = await aioamqp.connect(
                host=self.host,
                port=self.port,
                on_error=self.on_error_callback
            )
        except aioamqp.AmqpClosedConnection:
            logging.error('Connection lost with message broker.')
        except OSError:
            await asyncio.sleep(10)
            await self.connect()

        return protocol

    async def on_error_callback(self, exception):
        """Reconnect on RabbitMQ callback."""
        try:
            logging.error("Error to connect with message broker, a new attempt will occur in 10 seconds.")
            await asyncio.sleep(10)
            await self.connect()
        except aioamqp.exceptions.SynchronizationError:
            pass
        except Exception:
            pass

    async def _configure_pub_sub(self):
        self.publish.channel = self._channel
        self.subscribe.channel = self._channel
        self.dlx.channel = self._channel

    async def configure(self):
        logging.info('Configurando o message broker...')
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_bind()
        logging.info('Successfully.')

    async def configure_subscribe(self):
        await self.configure_subscribe_exchange()
        await self.subscribe.configure_queue()
        await self.dlx.configure_queue()
        await self.subscribe.configure_queue_bind()
        await self.dlx.configure_queue_bind()
    
    async def configure_publish(self):
        await self.publish.configure_exchange()
        await asyncio.sleep(2)
        await self.publish.configure_queue()
        await self.publish.configure_queue_bind()

    async def configure_subscribe_exchange(self):
        logging.info('Configurando as exchanges...')
        await self.subscribe.configure_exchange()
        await self.dlx.configure_exchange()
        await asyncio.sleep(2)
    
    async def configure_publish_exchange(self):
        logging.info('Configurando as exchanges...')
        await self.publish.configure_exchange()
        await asyncio.sleep(2)

    # async def configure_queue(self):
    #     logging.info('Configurando as queues...')
    #     await self.subscribe.configure_queue()
    #     await self.publish.configure_queue()
    #     await self.dlx.configure_queue()

    # async def configure_bind(self):
    #     logging.info('Configurando o binding das queues...')
    #     await self.subscribe.configure_queue_bind()
    #     await self.publish.configure_queue_bind()
    #     await self.dlx.configure_queue_bind()
