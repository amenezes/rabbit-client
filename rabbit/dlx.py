from typing import Any, Callable

import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)
from attrs import field, mutable, validators

from rabbit._wait import constant
from rabbit.exchange import Exchange
from rabbit.logger import logger
from rabbit.queue import Queue


@mutable
class DLX:
    exchange: Exchange = field(
        validator=validators.instance_of(Exchange),
    )
    dlq_exchange: Exchange = field(
        validator=validators.instance_of(Exchange),
    )
    queue: Queue = field(
        validator=validators.instance_of(Queue),
    )
    delay_strategy: Callable[..., int] = field(
        default=constant, validator=validators.is_callable()
    )
    _channel: AbstractChannel | None = field(default=None, init=False, repr=False)
    _dlx_exchange: AbstractExchange | None = field(default=None, init=False, repr=False)

    def __repr__(self) -> str:
        return (
            f"DLX(queue={self.queue}, delay_strategy={self.delay_strategy.__name__}, "
            f"exchange={self.exchange}), dlq_exchange={self.dlq_exchange}"
        )

    async def configure(
        self,
        channel: AbstractChannel,
        main_queue: AbstractQueue,
    ) -> None:
        self._channel = channel

        self._dlx_exchange = await channel.declare_exchange(
            self.exchange.name,
            ExchangeType(self.exchange.exchange_type),
            durable=self.exchange.durable,
        )

        dlq_router = await channel.declare_exchange(
            self.dlq_exchange.name,
            ExchangeType(self.dlq_exchange.exchange_type),
            durable=self.dlq_exchange.durable,
        )

        retry_queue_name = await self._ensure_endswith_dlq(self.queue.name)
        retry_queue = await channel.declare_queue(
            retry_queue_name,
            durable=self.queue.durable,
            arguments={
                "x-dead-letter-exchange": self.dlq_exchange.name,
                "x-dead-letter-routing-key": self.queue.name,
            },
        )

        await retry_queue.bind(self._dlx_exchange, routing_key=self.queue.name)
        await main_queue.bind(dlq_router, routing_key=self.queue.name)

    async def send_event(
        self, cause: Exception, message: AbstractIncomingMessage
    ) -> None:
        if self._dlx_exchange is None:
            raise RuntimeError("DLX not configured. Call configure() first.")

        delay = self.delay_strategy(message.headers)

        headers: dict[str, Any] = {
            "x-delay": str(delay),
            "x-exception-message": str(cause),
            "x-original-exchange": message.exchange or "",
            "x-original-routingKey": message.routing_key or "",
        }
        if message.headers:
            headers.update(message.headers)

        logger.debug(
            f"Send event to dlq: [exchange: {self.exchange.name}"
            f" | routing_key: {self.queue.name} | delay: {delay}]"
        )

        await self._dlx_exchange.publish(
            aio_pika.Message(
                body=message.body,
                expiration=int(delay),
                headers=headers,
            ),
            routing_key=self.queue.name,
        )

    async def _ensure_endswith_dlq(self, value: str) -> str:
        if not value.endswith(".dlq"):
            value = f"{value}.dlq"
        return value
