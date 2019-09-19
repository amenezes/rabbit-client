import asyncio
import json
import logging
import os

import aioamqp

import attr

from rabbit.callback import reconnect_callback


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
    _channel = attr.ib(default=None)
    error_callback = attr.ib(default=reconnect_callback)

    @property
    def channel(self):
        return self._channel

    @property
    def app(self):
        return self._app

    async def connect(self, auto_configure=True):
        protocol = await self._get_protocol_connection()
        self._channel = await protocol.channel()

    async def _get_protocol_connection(self):
        protocol = None
        try:
            *_, protocol = await aioamqp.connect(
                host=self.host,
                port=self.port,
                on_error=self.error_callback
                # on_error=self.on_error_callback
            )
        except aioamqp.AmqpClosedConnection:
            logging.error('Lost connection with message broker.')
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
