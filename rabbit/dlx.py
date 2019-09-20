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
    dlq_queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv('DQL_QUEUE', 'default.in.exchange.dlq'),
            arguments={
                'x-dead-letter-exchange': os.getenv(
                    'SUBSCRIBE_EXCHANGE', 'default.in.exchange'
                ),
                'x-dead-letter-routing-key': os.getenv(
                    'SUBSCRIBE_TOPIC', '#'
                )
            }
        ),
        validator=attr.validators.instance_of(Queue)
    )
    routing_key = attr.ib(
        type=str,
        default=os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange'),
        validator=attr.validators.instance_of(str)
    )
    properties = attr.ib(
        type=dict,
        default={
            'expiration': f'{5000}',
            'headers': {
                'x-delay': f'{5000}',
                'x-exception-message': '',
                'x-original-exchange': '',
                'x-original-routingKey': ''
            }
        },
        validator=attr.validators.instance_of(dict)
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
            queue_name=self.dlq_queue.name,
            durable=self.dlq_queue.durable,
            arguments=self.dlq_queue.arguments
        )

    async def _configure_queue_bind(self):
        await self.channel.queue_bind(
            exchange_name=self.dlx_exchange.name,
            queue_name=self.dlq_queue.name,
            routing_key=self.get_routing_key()
        )

    def get_routing_key(self, filter='.dlq'):
        return self.dlq_queue.name.split(filter)[0]

    async def send_event(self, cause, body, envelope, properties, subscribe_queue):
        logging.error(f'Error to process event: {cause}')
        await self.channel.publish(
            body,
            self.dlx_exchange.name,
            subscribe_queue,
            self.properties
        )
