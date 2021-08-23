import asyncio
import os
from contextlib import suppress
from typing import Callable

import attr
from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.exceptions import SynchronizationError
from aioamqp.properties import Properties

from rabbit import constant, logger
from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exceptions import AttributeNotInitialized
from rabbit.exchange import Exchange
from rabbit.queue import Queue


@attr.s(slots=True, repr=False)
class Subscribe:
    _client = attr.ib(
        type=AioRabbitClient,
        validator=attr.validators.instance_of(AioRabbitClient),
        repr=False,
    )
    task = attr.ib(type=Callable, validator=attr.validators.is_callable())
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv("SUBSCRIBE_EXCHANGE_NAME", "default.in.exchange"),
            exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", "topic"),
            topic=os.getenv("SUBSCRIBE_TOPIC", "#"),
        ),
        validator=attr.validators.instance_of(Exchange),
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv("SUBSCRIBE_QUEUE_NAME", "default.subscribe.queue")
        ),
        validator=attr.validators.instance_of(Queue),
    )
    concurrent = attr.ib(
        type=int, default=1, validator=attr.validators.instance_of(int)
    )
    delay = attr.ib(
        type=int,
        default=int(os.getenv("INITIAL_DELAY", 300000)),
        validator=attr.validators.instance_of(int),
    )
    delay_strategy = attr.ib(
        type=Callable, default=constant, validator=attr.validators.is_callable()
    )
    _dlx = attr.ib(type=DLX, validator=attr.validators.instance_of(DLX), init=False)
    _job_queue = attr.ib(init=False, repr=False)
    _loop = attr.ib(init=False, repr=False)
    _channel = attr.ib(init=False, repr=False)

    def __repr__(self) -> str:
        return f"Subscribe(task={self.task.__name__}, exchange={self.exchange}, queue={self.queue}, concurrent={self.concurrent}, dlx={self._dlx})"

    def __attrs_post_init__(self) -> None:
        self._dlx = DLX(
            client=self._client,
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
            delay=self.delay,
        )
        self._job_queue = asyncio.Queue(maxsize=self.concurrent)
        self._loop = asyncio.get_event_loop()

    async def configure(self) -> None:
        await asyncio.sleep(5)
        self._channel = await self._client.get_channel()
        await self.qos(prefetch_count=self.concurrent)
        # self._loop.create_task(self._client.watch(self), name="subscribe_watcher")
        self._loop.create_task(self._client.watch(self))
        with suppress(SynchronizationError):
            try:
                await self._configure_queue()
                await self._dlx.configure()
                await self._configure_exchange()
                await self._configure_queue_bind()
            except AttributeNotInitialized:
                logger.debug("Waiting client initialization...SUBSCRIBE")

    async def _configure_exchange(self) -> None:
        await self._channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable,
        )
        await asyncio.sleep(2)

    async def _configure_queue(self) -> None:
        await self._channel.queue_declare(
            queue_name=self.queue.name, durable=self.queue.durable
        )

    async def _configure_queue_bind(self) -> None:
        await self._channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic,
        )
        await self._channel.basic_consume(
            callback=self.callback, queue_name=self.queue.name
        )

    async def callback(
        self, channel: Channel, body: bytes, envelope: Envelope, properties: Properties
    ) -> None:
        if not self._job_queue.full():
            self._job_queue.put_nowait((body, envelope, properties))
            self._loop.create_task(self._run())
        else:
            await self.nack_event(envelope, requeue=True)
            await self._job_queue.join()

    async def _run(self) -> None:
        try:
            body, envelope, properties = await self._job_queue.get()
            await self.task(body)
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
        await self._channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag, multiple=multiple
        )

    async def nack_event(
        self, envelope: Envelope, multiple: bool = False, requeue: bool = True
    ) -> None:
        await self._channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag, multiple=multiple, requeue=requeue
        )

    async def reject_event(self, envelope: Envelope, requeue: bool = False) -> None:
        await self._channel.basic_reject(
            delivery_tag=envelope.delivery_tag, requeue=requeue
        )

    async def qos(
        self,
        prefetch_size: int = 0,
        prefetch_count: int = 0,
        connection_global: bool = False,
    ):
        await self._channel.basic_qos(
            prefetch_size=prefetch_size,
            prefetch_count=prefetch_count,
            connection_global=connection_global,
        )
