from typing import Callable

from aio_pika import ExchangeType
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)
from attrs import field, mutable, validators

from rabbit._wait import constant
from rabbit.dlx import DLX
from rabbit.exceptions import ClientNotConnectedError
from rabbit.exchange import Exchange
from rabbit.logger import logger
from rabbit.queue import Queue


@mutable(repr=False)
class Subscribe:
    task: Callable = field(validator=validators.is_callable())
    exchange: Exchange = field(
        default=Exchange(
            name="default.in.exchange",
            exchange_type="topic",
            topic="#",
        ),
        validator=validators.instance_of(Exchange),
    )
    queue: Queue = field(
        default=Queue(name="default.subscribe.queue"),
        validator=validators.instance_of(Queue),
    )
    concurrent: int = field(default=1, validator=validators.instance_of(int))
    delay_strategy: Callable = field(
        default=constant, validator=validators.is_callable()
    )
    _dlx: DLX = field(validator=validators.instance_of(DLX), init=False)
    _channel: AbstractChannel | None = field(default=None, init=False)
    _main_exchange: AbstractExchange | None = field(default=None, init=False)
    _main_queue: AbstractQueue | None = field(default=None, init=False)

    def __repr__(self) -> str:
        return (
            f"Subscribe(task={self.task.__name__}, exchange={self.exchange}, "
            f"queue={self.queue}, concurrent={self.concurrent})"
        )

    def __attrs_post_init__(self) -> None:
        self._dlx = DLX(
            exchange=Exchange(
                name="DLX",
                exchange_type="direct",
            ),
            dlq_exchange=Exchange(
                name=f"dlqReRouter.{self.exchange.name}",
                exchange_type="topic",
                topic=self.queue.name,
            ),
            queue=Queue(
                name=self.queue.name,
                arguments={
                    "x-dead-letter-exchange": f"dlqReRouter.{self.exchange.name}",
                    "x-dead-letter-routing-key": self.queue.name,
                },
            ),
            delay_strategy=self.delay_strategy,
        )

    @property
    def name(self) -> str:
        return "Subscribe"

    @property
    def channel(self) -> AbstractChannel:
        if self._channel is None:
            raise ClientNotConnectedError
        return self._channel

    @channel.setter
    def channel(self, channel: AbstractChannel) -> None:
        self._channel = channel

    async def configure(self, channel: AbstractChannel | None = None) -> None:
        if channel is not None:
            self.channel = channel

        ch = self.channel

        await ch.set_qos(prefetch_count=self.concurrent)

        self._main_exchange = await ch.declare_exchange(
            self.exchange.name,
            ExchangeType(self.exchange.exchange_type),
            durable=self.exchange.durable,
        )
        self._main_queue = await ch.declare_queue(
            self.queue.name,
            durable=self.queue.durable,
        )
        await self._main_queue.bind(
            self._main_exchange, routing_key=self.exchange.topic
        )
        await self._dlx.configure(ch, self._main_queue)

        await self._main_queue.consume(self._handle_message)

    async def _handle_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(
            requeue=False,
            ignore_processed=True,
        ):
            try:
                await self.task(message)
                await message.ack()
            except Exception as cause:
                logger.warning(
                    f"Task failed for message (delivery_tag={message.delivery_tag}): {cause}"
                )
                try:
                    await self._dlx.send_event(cause, message)
                except Exception:
                    logger.warning("DLQ send failed in error path", exc_info=True)
                await message.ack()
