import asyncio
import os
import json

import attr

import aioamqp


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Setup:

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

    async def connect(self, auto_configure=True):
        protocol = await self._get_protocol_connection()
        self._channel = await protocol.channel()

    async def _get_protocol_connection(self):
        protocol = None
        try:
            *_, protocol = await aioamqp.connect(
                host=self.host,
                port=self.port,
                on_error=self.on_error_callback
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
            logger.error("Error to connect with message broker, a new attempt will occur in 10 seconds.")
            await asyncio.sleep(10)
            await self.connect()
        except aioamqp.exceptions.SynchronizationError:
            pass

    async def callback(self, channel, body, envelope, properties):
        """Trigger for the processing of parts."""
        try:
            payload = json.loads(body)
            await self.handler.process(payload)
            await event.ack(self._channel, envelope)
            await asyncio.sleep(5)
        except Exception as cause:
            await self.process_error(cause, body, envelope, properties)

    async def process_error(self, exception_type, body, envelope, properties):
        logger.error(f'Erro ao processar o evento: {exception_type}')
        timeout = await event.get_timeout(properties.headers)
        await event.publish(
            self._channel,
            body,
            getattr(settings, 'dlx_exchange'),
            getattr(settings, 'subscribe_queue'),
            {
                'expiration': f'{timeout}',
                'headers': {
                    'x-delay': f'{timeout}',
                    'x-exception-message': f'{exception_type}',
                    'x-original-exchange': f'{envelope.exchange_name}',
                    'x-original-routingKey': f'{envelope.routing_key}'
                }
            }
        )
        await event.reject(self._channel, envelope)
