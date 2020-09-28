import asyncio
import os
from contextlib import suppress

import attr
from aioamqp.exceptions import SynchronizationError

from rabbit import logger
from rabbit.client import AioRabbitClient
from rabbit.exceptions import AttributeNotInitialized
from rabbit.exchange import Exchange


@attr.s(slots=True)
class Publish:

    _client = attr.ib(
        type=AioRabbitClient, validator=attr.validators.instance_of(AioRabbitClient)
    )
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv("PUBLISH_EXCHANGE", "default.out.exchange"),
            exchange_type=os.getenv("PUBLISH_EXCHANGE_TYPE", "topic"),
            topic=os.getenv("PUBLISH_TOPIC", "#"),
        ),
        validator=attr.validators.instance_of(Exchange),
    )

    def __attrs_post_init__(self) -> None:
        self._client.watch(self)

    async def configure(self) -> None:
        with suppress(SynchronizationError):
            try:
                await self._configure_exchange()
            except AttributeNotInitialized:
                logger.debug("Waiting client initialization...PUBLISH")

    async def _configure_exchange(self) -> None:
        await self._client.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(2)

    async def send_event(self, payload: bytes, **kwargs) -> None:
        await self._client.channel.publish(
            payload=payload,
            exchange_name=self.exchange.name,
            routing_key=self.exchange.topic,
            **kwargs,
        )
