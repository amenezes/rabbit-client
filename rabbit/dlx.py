import asyncio
import logging
import os

from aioamqp.channel import Channel

import attr

from rabbit.exchange import Exchange
from rabbit.queue import Queue


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class DLX:

    dlq_queue = attr.ib(
        type=Queue,
        validator=attr.validators.instance_of(Queue)
    )
    routing_key = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    channel = attr.ib(
        type=Channel,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Channel)
        )
    )
    dlx_exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('DLX_EXCHANGE', 'DLX'),
            exchange_type=os.getenv('DLX_TYPE', 'direct')
        ),
        validator=attr.validators.instance_of(Exchange)
    )

    async def configure(self):
        await self._configure_exchange()
        await self._configure_queue()
        await self._configure_queue_bind()

    async def _configure_exchange(self):
        await self.channel.exchange_declare(
            exchange_name=self.dlx_exchange.name,
            type_name=self.dlx_exchange.exchange_type,
            durable=self.dlx_exchange.durable
        )
        asyncio.sleep(2)

    async def _configure_queue(self):
        await self.channel.queue_declare(
            queue_name=self._ensure_endswith_dlq(self.dlq_queue.name),
            durable=self.dlq_queue.durable,
            arguments=self.dlq_queue.arguments
        )

    async def _configure_queue_bind(self):
        await self.channel.queue_bind(
            exchange_name=self.dlx_exchange.name,
            queue_name=self._ensure_endswith_dlq(self.dlq_queue.name),
            routing_key=self.routing_key
        )

    def _remove_invalid_queue_extension(self, value):
        if value.rfind('.') > 0:
            value = value.replace(
                value[value.rfind('.'):],
                ''
            )
        return value

    def _ensure_endswith_dlq(self, value):
        if not value.endswith('.dlq'):
            value = f'{value}.dlq'
        return value

    def _get_properties(self,
                        timeout,
                        exception_message,
                        original_exchange,
                        original_routing_key):
        properties = {
            'expiration': f'{timeout}',
            'headers': {
                'x-delay': f'{timeout}',
                'x-exception-message': f'{exception_message}',
                'x-original-exchange': f'{original_exchange}',
                'x-original-routingKey': f'{original_routing_key}'
            }
        }
        return properties

    async def send_event(self, cause, body, envelope, properties):
        logging.error(f'Error to process event: {cause}')
        timeout = await self._get_timeout(properties.headers)
        await self.channel.publish(
            body,
            self.dlx_exchange.name,
            self.dlq_queue.name,
            self._get_properties(
                timeout,
                cause,
                envelope.exchange_name,
                envelope.routing_key
            )
        )

    async def _get_timeout(self, headers, delay=5000):
        if (headers is not None) and ('x-delay' in headers):
            delay = headers['x-delay']
        return int(delay) * 5
