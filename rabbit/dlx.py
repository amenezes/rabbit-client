import asyncio
from typing import Callable

from aioamqp.envelope import Envelope
from aioamqp.properties import Properties
from attrs import field, mutable, validators

from ._wait import constant
from .client import AioRabbitClient
from .exceptions import AttributeNotInitialized, OperationError
from .exchange import Exchange
from .logger import logger
from .queue import Queue


@mutable
class DLX:
    _client: AioRabbitClient = field(
        validator=validators.instance_of(AioRabbitClient),
        repr=False,
    )
    exchange: Exchange = field(
        validator=validators.instance_of(Exchange),
    )
    dlq_exchange: Exchange = field(
        validator=validators.instance_of(Exchange),
    )
    queue: Queue = field(
        validator=validators.instance_of(Queue),
    )
    delay_strategy: Callable = field(
        default=constant, validator=validators.is_callable()
    )
    _channel = field(init=False, repr=False)

    def __repr__(self) -> str:
        return f"DLX(queue={self.queue}, delay_strategy={self.delay_strategy.__name__}, exchange={self.exchange}), dlq_exchange={self.dlq_exchange}"

    async def configure(self) -> None:
        self._channel = await self._client.get_channel()
        try:
            await self._configure_queue()
            await self._configure_exchange()
            await self._configure_queue_bind()
        except AttributeNotInitialized:
            logger.debug("Waiting client initialization...DLX")

    async def _configure_exchange(self) -> None:
        await asyncio.gather(
            self._channel.exchange_declare(
                exchange_name=self.exchange.name,
                type_name=self.exchange.exchange_type,
                durable=self.exchange.durable,
            ),
            self._channel.exchange_declare(
                exchange_name=self.dlq_exchange.name,
                type_name=self.dlq_exchange.exchange_type,
                durable=self.dlq_exchange.durable,
            ),
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
        await asyncio.gather(
            self._channel.queue_bind(
                exchange_name=self.exchange.name,
                queue_name=queue_name,
                routing_key=self.queue.name,
            ),
            self._channel.queue_bind(
                exchange_name=self.dlq_exchange.name,
                queue_name=self.queue.name,
                routing_key=self.dlq_exchange.topic,
            ),
        )

    async def _ensure_endswith_dlq(self, value: str) -> str:
        if not value.endswith(".dlq"):
            value = f"{value}.dlq"
        return value

    async def send_event(
        self, cause: Exception, body: bytes, envelope: Envelope, properties: Properties
    ) -> None:
        timeout = self.delay_strategy(properties.headers)
        properties = await self._get_properties(timeout, cause, envelope)

        logger.debug(
            f"Send event to dlq: [exchange: {self.exchange.name}"
            f" | routing_key: {self.queue.name} | properties: {properties}]"
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
