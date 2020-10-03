import asyncio
import os
from contextlib import suppress
from typing import Any, Callable, Optional

import attr
from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.exceptions import SynchronizationError
from aioamqp.properties import Properties

from rabbit import logger
from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exceptions import AttributeNotInitialized
from rabbit.exchange import Exchange
from rabbit.queue import Queue


@attr.s
class Subscribe:

    client = attr.ib(
        type=AioRabbitClient, validator=attr.validators.instance_of(AioRabbitClient)
    )
    task = attr.ib(type=Callable, validator=attr.validators.is_callable())
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv("SUBSCRIBE_EXCHANGE", "default.in.exchange"),
            exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", "topic"),
            topic=os.getenv("SUBSCRIBE_TOPIC", "#"),
        ),
        validator=attr.validators.instance_of(Exchange),
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(name=os.getenv("SUBSCRIBE_QUEUE", "default.subscribe.queue")),
        validator=attr.validators.instance_of(Queue),
    )
    dlx = attr.ib(
        type=Optional[DLX],
        default=None,
        validator=attr.validators.optional(validator=attr.validators.instance_of(DLX)),
    )
    func = attr.ib(
        type=Callable,
        default=None,
        validator=attr.validators.optional(validator=attr.validators.is_callable()),
    )

    def __attrs_post_init__(self) -> None:
        self.client.watch(self)
        if not self.dlx:
            self.dlx = DLX(self.client)

    async def configure(self) -> None:
        await asyncio.sleep(5)
        with suppress(SynchronizationError):
            try:
                if self.dlx:
                    await self.dlx.configure()
                await self._configure_exchange()
                await self._configure_queue()
                await self._configure_queue_bind()
            except AttributeNotInitialized:
                logger.debug("Waiting client initialization...SUBSCRIBE")

    async def _configure_exchange(self) -> None:
        await self.client.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(5)

    async def _configure_queue(self) -> None:
        await self.client.channel.queue_declare(
            queue_name=self.queue.name, durable=self.queue.durable
        )

    async def _configure_queue_bind(self) -> None:
        await self.client.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic,
        )
        await self.client.channel.basic_consume(
            callback=self.callback, queue_name=self.queue.name
        )

    async def callback(
        self, channel: Channel, body: bytes, envelope: Envelope, properties: Properties
    ) -> Optional[Any]:
        result = None
        try:
            await self.ack_event(envelope)
            result = await self.task(body)
            if self.func:
                await self.func(body, result)
        except Exception as cause:
            logger.error(cause)
            if self.dlx:
                await self.dlx.send_event(cause, body, envelope, properties)
        return result

    async def reject_event(self, envelope: Envelope, requeue: bool = False) -> None:
        await self.client.channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag, requeue=requeue
        )

    async def ack_event(self, envelope: Envelope) -> None:
        await self.client.channel.basic_client_ack(delivery_tag=envelope.delivery_tag)
