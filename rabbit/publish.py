import asyncio
import logging
import os
from typing import Optional

import attr

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.queue import Queue


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Publish:

    _client = attr.ib(
        type=Optional[AioRabbitClient],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(AioRabbitClient)
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

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        if not isinstance(client, AioRabbitClient):
            raise ValueError('client must be AioRabbitClient instance.')
        self._client = client
        self._client.instances.append(self)

    async def configure(self) -> None:
        if not self.client.channel:
            await self.client.connect()
        await self._configure_exchange()
        await self._configure_queue()
        await self._configure_queue_bind()

    async def _configure_exchange(self) -> None:
        logging.debug(
            "Configuring Publish exchange: ["
            f"exchange_name: {self.exchange.name}] | "
            f"type_name: {self.exchange.exchange_type}"
            f" | durable: {self.exchange.durable}]"
        )
        await self.client.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable
        )
        await asyncio.sleep(2)

    async def _configure_queue(self) -> None:
        logging.debug(
            "Configuring Publish queue: ["
            f"queue_name: {self.queue.name}] | "
            f"durable: {self.queue.durable}]"
        )
        await self.client.channel.queue_declare(
            queue_name=self.queue.name,
            durable=self.queue.durable
        )

    async def _configure_queue_bind(self) -> None:
        logging.debug(
            "Configuring Publish queue bind: ["
            f"exchange_name: {self.exchange.name}] | "
            f"queue_name: {self.queue.name}"
            f" | routing_key: {self.exchange.topic}]"
        )
        await self.client.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )

    async def send_event(self, payload: bytes, **kwargs) -> None:
        await self.client.channel.publish(
            payload=payload,
            exchange_name=self.exchange.name,
            routing_key=self.exchange.topic,
            **kwargs
        )
