import os

import attr

from rabbit.queue import Queue
from rabbit.exchange import Exchange


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Publish:

    channel = attr.ib()
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('PUBLISH_EXCHANGE', 'default.publish.exchange'),
            exchange_type=os.getenv('PUBLISH_EXCHANGE_TYPE', 'topic')
            topic=os.getenv('PUBLISH_TOPIC', '#')
        ),
        validator=attr.validators.instance_of(Exchange)
    )
    dlx_exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('DLX_EXCHANGE', 'DLX'),
            exchange_type=os.getenv('DLX_TYPE', 'direct')
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
        await self.configure_exchange()
        await self.configure_queue()

    async def configure_exchange(self):
        await self.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable
        )
        await self.channel.exchange_declare(
            exchange_name=self.dlx_exchange.name,
            type_name=self.dlx_exchange.exchange_type,
            durable=self.dlx_exchange.durable
        )

    async def configure_queue(self):
        await self.channel.queue_declare(
            queue_name=self.queue.name,
            durable=self.queue.durable
    )

    async def configure_bind(self):
        await channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )
        await channel.queue_bind(
            exchange_name=self.dlx_exchange.name,
            queue_name=self.dlx_exchange.name,
            routing_key=self.dlx_exchange.topic
        )
