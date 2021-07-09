import asyncio
import os
from typing import Callable

import attr
from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

from rabbit import constant, logger
from rabbit.client import AioRabbitClient
from rabbit.exceptions import AttributeNotInitialized, OperationError
from rabbit.exchange import Exchange
from rabbit.queue import Queue


@attr.s(slots=True)
class DLX:
    _client = attr.ib(
        type=AioRabbitClient,
        validator=attr.validators.instance_of(AioRabbitClient),
        repr=False,
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv("SUBSCRIBE_QUEUE", "default.subscribe.queue"),
            arguments={
                "x-dead-letter-exchange": os.getenv(
                    "SUBSCRIBE_EXCHANGE", "default.in.exchange"
                ),
                "x-dead-letter-routing-key": os.getenv("SUBSCRIBE_TOPIC", "#"),
            },
        ),
        validator=attr.validators.instance_of(Queue),
    )
    routing_key = attr.ib(
        type=str,
        default=os.getenv("SUBSCRIBE_QUEUE", "default.subscribe.queue"),
        validator=attr.validators.instance_of(str),
    )
    delay_strategy = attr.ib(
        type=Callable, default=constant, validator=attr.validators.is_callable()
    )
    delay = attr.ib(
        type=int,
        default=int(os.getenv("INITIAL_DELAY", 300000)),
        validator=attr.validators.instance_of(int),
    )
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv("DLX_EXCHANGE", "DLX"),
            exchange_type=os.getenv("DLX_TYPE", "direct"),
        ),
        validator=attr.validators.instance_of(Exchange),
    )
    _channel = attr.ib(init=False, repr=False)

    async def configure(self) -> None:
        self._channel = await self._client.get_channel()
        try:
            await self._configure_exchange()
            await self._configure_queue()
            await self._configure_queue_bind()
        except AttributeNotInitialized:
            logger.debug("Waiting client initialization...DLX")

    async def _configure_exchange(self) -> None:
        await self._channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(2)

    async def _configure_queue(self) -> None:
        queue_name = await self._ensure_endswith_dlq(self.queue.name)
        await self._channel.queue_declare(
            queue_name=queue_name,
            durable=self.queue.durable,
            arguments=self.queue.arguments,
        )

    async def _configure_queue_bind(self) -> None:
        queue_name = await self._ensure_endswith_dlq(self.queue.name)
        await self._channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=queue_name,
            routing_key=self.routing_key,
        )

    async def _ensure_endswith_dlq(self, value: str) -> str:
        if not value.endswith(".dlq"):
            value = f"{value}.dlq"
        return value

    async def send_event(
        self, cause: Exception, body: bytes, envelope: Envelope, properties: Properties
    ) -> None:
        timeout = self.delay_strategy(properties.headers, self.delay)
        properties = await self._get_properties(timeout, cause, envelope)

        logger.debug(f"Timeout: {timeout}")
        logger.debug(
            f"Send event to dlq: [exchange: {self.exchange.name}"
            f" | queue: {self.queue.name} | properties: {properties}]"
        )
        try:
            await self._channel.publish(
                body, self.exchange.name, self.queue.name, properties
            )
        except AttributeError:
            raise OperationError("Ensure that instance was connected ")

    async def _get_properties(
        self, timeout: int, exception_message: Exception, envelope: Envelope
    ) -> dict:
        return {
            "expiration": f"{timeout}",
            "headers": {
                "x-delay": f"{timeout}",
                "x-exception-message": f"{exception_message}",
                "x-original-exchange": f"{envelope.exchange_name}",
                "x-original-routingKey": f"{envelope.routing_key}",
            },
        }
