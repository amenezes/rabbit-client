import asyncio
import logging
import os

from aioamqp.channel import Channel

import attr

from rabbit.exchange import Exchange
from rabbit.queue import Queue

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Publish:

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
            name=os.getenv('PUBLISH_EXCHANGE', 'default.out.exchange'),
            exchange_type=os.getenv('PUBLISH_EXCHANGE_TYPE', 'topic'),
            topic=os.getenv('PUBLISH_TOPIC', '#')
        ),
        validator=attr.validators.instance_of(Exchange)
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv('PUBLISH_QUEUE', 'default.publish.queue')
        ),
        validator=attr.validators.instance_of(Queue)
    )

    async def configure(self):
        await self._configure_exchange()
        await self._configure_queue()
        await self._configure_queue_bind()

    async def _configure_exchange(self):
        await self.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable
        )
        await asyncio.sleep(2)

    async def _configure_queue(self):
        await self.channel.queue_declare(
            queue_name=self.queue.name,
            durable=self.queue.durable
        )

    async def _configure_queue_bind(self):
        await self.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )

    async def send_event(self, payload, **kwargs):
        await self.channel.publish(
            payload=payload,
            exchange_name=self.exchange.name,
            routing_key=self.exchange.topic,
            **kwargs
        )
