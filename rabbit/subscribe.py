import asyncio
import logging
import os

from aioamqp.channel import Channel

import attr

from rabbit.dlx import DLX
from rabbit.exchange import Exchange
from rabbit.queue import Queue
from rabbit.task import Task


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
    dlx = attr.ib(
        type=DLX,
        default=DLX(),
        validator=attr.validators.instance_of(DLX)
    )
    task = attr.ib(
        type=Task,
        default=Task()
    )

    async def configure(self):
        await self._configure_exchange()
        await self._configure_queue()
        await self._configure_queue_bind()
        await self._configure_dlx()

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
        await self.channel.basic_consume(
            callback=self.callback,
            queue_name=self.queue.name
        )

    async def _configure_dlx(self):
        self.dlx.channel = self.channel
        await self.dlx.configure()

    async def callback(self, channel, body, envelope, properties):
        print(channel)
        print(body)
        print(envelope)
        print(properties)
        try:
            await self.task.execute(body)
            await self.ack_event(envelope)
        except Exception as cause:
            await self.dlx.send_event(cause, body, envelope, properties, self.queue.name)
            await self.reject_event(envelope)

    async def reject_event(self, envelope, requeue=False):
        await self.channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag,
            requeue=requeue
        )

    async def ack_event(self, envelope):
        await self.channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag
        )
