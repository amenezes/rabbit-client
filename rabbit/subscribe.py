import logging
import os

from aioamqp.channel import Channel

import attr

from rabbit.callback import process_event_callback
from rabbit.exchange import Exchange
from rabbit.queue import Queue


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Subscribe:

    channel = attr.ib(
        type=Channel,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Channel)
        )
    )
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange'),
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
    callback = attr.ib(default=process_event_callback)

    async def configure(self):
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_queue_bind()

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

    async def configure_queue_bind(self):
        await self.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )
        await self.channel.basic_consume(
            callback=self.callback,
            queue_name=self.queue.name
        )
