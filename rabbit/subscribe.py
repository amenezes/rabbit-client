import logging
import os

import attr

from rabbit.queue import Queue
from rabbit.exchange import Exchange


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Subscribe:

    channel = attr.ib()
    callback = attr.ib()
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('SUBSCRIBE_EXCHANGE', 'default.exchange'),
            exchange_type=os.getenv('SUBSCRIBE_EXCHANGE_TYPE', 'topic'),
            topic=os.getenv('SUBSCRIBE_TOPIC', '#')
        ),
        validator=attr.validators.instance_of(Exchange)
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')
        ),
        validator=attr.validators.instance_of(Queue)
    )
    dlq_queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv('DQL_QUEUE', f'{exchange.name}{suffix}'),
            suffix='.dlq',
            arguments={
                'x-dead-letter-exchange': os.getenv('SUBSCRIBE_EXCHANGE', 'default.exchange'),
                'x-dead-letter-routing-key': os.getenv('SUBSCRIBE_TOPIC', '#')
            }
        ),
        validator=attr.validators.instance_of(Queue)
    )

    async def configure(self):
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_bind()

    async def configure_exchange(self):
        await self.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable
        )
    
    async def configure_queue(self):
        await self.channel.queue_declare(
            queue_name=self.queue.name,
            durable=self.queue.durable
        )
        if enable_dlq:
            await self.configure_dlq_queue()
    
    async def configure_dlq_queue(self):
        await self.channel.queue_declare(
            queue_name=self.dlq_queue.name,
            durable=self.dlq_queue.durable,
            arguments=self.dlq_queue.arguments
    )

    async def configure_bind(self):
        await self.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )
        await self.channel.basic_consume(
            callback=self.callback,
            queue_name=self.queue.name
        )
