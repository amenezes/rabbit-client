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
        type=AioRabbitClient,
        validator=attr.validators.instance_of(AioRabbitClient),
        repr=False,
    )
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv("PUBLISH_EXCHANGE", "default.in.exchange"),
            exchange_type=os.getenv("PUBLISH_EXCHANGE_TYPE", "topic"),
            topic=os.getenv("PUBLISH_TOPIC", "#"),
        ),
        validator=attr.validators.instance_of(Exchange),
    )
    _channel = attr.ib(init=False, repr=False)

    async def configure(self) -> None:
        await asyncio.sleep(1)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        # loop.create_task(self._client.watch(self), name="publish_watcher")
        loop.create_task(self._client.watch(self))
        with suppress(SynchronizationError):
            try:
                await self._configure_exchange()
            except AttributeNotInitialized:
                logger.debug("Waiting client initialization...PUBLISH")

    async def _configure_exchange(self) -> None:
        await self._channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(2)

    async def send_event(self, payload: bytes, **kwargs) -> None:
        await self._channel.publish(
            payload=payload,
            exchange_name=self.exchange.name,
            routing_key=self.exchange.topic,
            **kwargs,
        )
