import asyncio
import json
import logging
import os

import aioamqp
from aioamqp.channel import Channel

import attr

from rabbit.callback import reconnect_callback
from rabbit.client import AioRabbitClient


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitEngine:

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
    client = attr.ib(
        type=AioRabbitClient,
        default=AioRabbitClient(),
        validator=attr.validators.instance_of(AioRabbitClient)
    )
    _channel = attr.ib(
        type=Channel,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Channel)
        )
    )

    async def connect(self):
        protocol = await self._get_protocol_connection()
        self._channel = await protocol.channel()
        self.client.publish.channel = self._channel
        self.client.subscribe.channel = self._channel
        self.client.dlx.channel = self._channel
        # await self.configure()

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

    async def callback(self, channel, body, envelope, properties):
        """Trigger for the processing of parts."""
        try:
            payload = json.loads(body)
            logging.info(payload)
            await asyncio.sleep(5)
        except Exception as cause:
            await self.process_error(cause, body, envelope, properties)

    async def process_error(self, exception_type, body, envelope, properties):
        logging.error(f'Erro ao processar o evento: {exception_type}')

    async def configure(self):
        logging.info('Configurando o message broker...')
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_bind()
        logging.info('Successfully.')

    async def configure_exchange(self):
        logging.info('Configurando as exchanges...')
        await self.client.subscribe.configure_exchange()
        await self.client.publish.configure_exchange()
        await self.client.dlx.configure_exchange()
        await asyncio.sleep(2)

    async def configure_queue(self):
        logging.info('Configurando as queues...')
        await self.client.subscribe.configure_queue()
        await self.client.publish.configure_queue()
        await self.client.dlx.configure_queue()

    async def configure_bind(self):
        logging.info('Configurando o binding das queues...')
        await self.client.subscribe.configure_queue_bind()
        await self.client.publish.configure_queue_bind()
        await self.client.dlx.configure_queue_bind()