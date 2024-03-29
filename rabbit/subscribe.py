import asyncio
import os
from contextlib import suppress
from typing import Callable, Union

from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.exceptions import SynchronizationError
from aioamqp.properties import Properties
from attrs import field, mutable, validators

from ._wait import constant
from .dlx import DLX
from .exceptions import ClientNotConnectedError
from .exchange import Exchange
from .queue import Queue


@mutable(repr=False)
class Subscribe:
    task: Callable = field(validator=validators.is_callable())
    exchange: Exchange = field(
        default=Exchange(
            name=os.getenv("SUBSCRIBE_EXCHANGE_NAME", "default.in.exchange"),
            exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", "topic"),
            topic=os.getenv("SUBSCRIBE_TOPIC", "#"),
        ),
        validator=validators.instance_of(Exchange),
    )
    queue: Queue = field(
        default=Queue(
            name=os.getenv("SUBSCRIBE_QUEUE_NAME", "default.subscribe.queue")
        ),
        validator=validators.instance_of(Queue),
    )
    concurrent: int = field(default=1, validator=validators.instance_of(int))
    delay_strategy: Callable = field(
        default=constant, validator=validators.is_callable()
    )
    _dlx: DLX = field(validator=validators.instance_of(DLX), init=False)
    _job_queue = field(init=False)
    _loop = field(init=False)
    _channel: Channel = field(init=False)

    def __repr__(self) -> str:
        return f"Subscribe(task={self.task.__name__}, exchange={self.exchange}, queue={self.queue}, concurrent={self.concurrent}, dlx={self._dlx})"

    def __attrs_post_init__(self) -> None:
        self._dlx = DLX(
            exchange=Exchange(
                name=os.getenv("DLX_EXCHANGE_NAME", "DLX"),
                exchange_type=os.getenv("DLX_TYPE", "direct"),
            ),
            dlq_exchange=Exchange(
                name=os.getenv(
                    "DLQ_EXCHANGE_NAME", f"dlqReRouter.{self.exchange.name}"
                ),
                exchange_type=os.getenv("DLQ_EXCHANGE_TYPE", "topic"),
                topic=os.getenv("SUBSCRIBE_QUEUE", self.queue.name),
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
        self._job_queue = asyncio.Queue(maxsize=self.concurrent)
        self._loop = asyncio.get_running_loop()

    @property
    def name(self) -> str:
        return "Subscribe"

    @property
    def channel(self) -> Channel:
        try:
            return self._channel
        except AttributeError:
            raise ClientNotConnectedError

    @channel.setter
    def channel(self, channel: Channel) -> None:
        self._dlx.channel = channel
        self._channel = channel

    async def configure(self, channel: Union[None, Channel] = None) -> None:
        """Configure subscriber channel, queues and exchange."""
        await self.qos(prefetch_count=self.concurrent)
        with suppress(SynchronizationError):
            await asyncio.gather(self._configure_queue(), self._dlx.configure())
            await self._configure_exchange()
            await self._configure_queue_bind()

    async def _configure_exchange(self) -> None:
        await self.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(1.5)

    async def _configure_queue(self) -> None:
        await self.channel.queue_declare(
            queue_name=self.queue.name, durable=self.queue.durable
        )

    async def _configure_queue_bind(self) -> None:
        await self.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic,
        )
        await self.channel.basic_consume(
            callback=self.callback, queue_name=self.queue.name
        )

    async def callback(
        self, channel: Channel, body: bytes, envelope: Envelope, properties: Properties
    ) -> None:
        if not self._job_queue.full():
            self._job_queue.put_nowait((body, envelope, properties))
            self._loop.create_task(self._run(), name="subscribe-task")
        else:
            await self.nack_event(envelope, requeue=True)
            await self._job_queue.join()

    async def _run(self) -> None:
        try:
            body, envelope, properties = await self._job_queue.get()
            await self.task(body, envelope, properties)
            self._job_queue.task_done()
            await self.ack_event(envelope, multiple=False)
        except Exception as cause:
            await asyncio.shield(
                asyncio.gather(
                    self.ack_event(envelope, multiple=False),
                    self._dlx.send_event(cause, body, envelope, properties),
                )
            )

    async def ack_event(self, envelope: Envelope, multiple: bool = False) -> None:
        """Sends ack message to broker."""
        await self.channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag, multiple=multiple
        )

    async def nack_event(
        self, envelope: Envelope, multiple: bool = False, requeue: bool = True
    ) -> None:
        """Sends nack message to broker."""
        await self.channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag, multiple=multiple, requeue=requeue
        )

    async def reject_event(self, envelope: Envelope, requeue: bool = False) -> None:
        """Informs for the message broker that event message was rejected."""
        await self.channel.basic_reject(
            delivery_tag=envelope.delivery_tag, requeue=requeue
        )

    async def qos(
        self,
        prefetch_size: int = 0,
        prefetch_count: int = 0,
        connection_global: bool = False,
    ) -> None:
        """Configure qos feature in the subscriber channel."""
        await self.channel.basic_qos(
            prefetch_size=prefetch_size,
            prefetch_count=prefetch_count,
            connection_global=connection_global,
        )
