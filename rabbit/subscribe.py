import asyncio
import json
import logging
import os
from contextlib import suppress
from typing import Any, Optional

import attr
from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.exceptions import SynchronizationError
from aioamqp.properties import Properties

from rabbit import AttributeNotInitialized
from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exchange import Exchange
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.task import Task
from rabbit.tlog.db import DB

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Subscribe:

    client = attr.ib(
        type=AioRabbitClient, validator=attr.validators.instance_of(AioRabbitClient)
    )
    task = attr.ib(type=Task, validator=attr.validators.instance_of(Task))
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
    _publish = attr.ib(
        type=Optional[Publish],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Publish)
        ),
    )
    _db = attr.ib(
        type=Optional[DB],
        default=None,
        validator=attr.validators.optional(validator=attr.validators.instance_of(DB)),
    )

    def __attrs_post_init__(self) -> None:
        self.client.watch(self)
        if not self.dlx:
            self.dlx = DLX(self.client)

    async def configure(self) -> None:
        with suppress(SynchronizationError):
            await asyncio.sleep(5)
            try:
                if self.dlx:
                    await self.dlx.configure()
                await self._configure_exchange()
                await self._configure_queue()
                await self._configure_publish()
                await self._configure_queue_bind()
            except AttributeNotInitialized:
                logging.debug("Waiting client initialization...SUBSCRIBE")

    async def _configure_publish(self) -> None:
        if self._publish:
            await self._publish.configure()

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
    ):
        process_result = [bytes()]
        try:
            await self.ack_event(envelope)
            process_result = await self._execute(body)
            if self._publish:
                for result in process_result:
                    await self._publish.send_event(result)
            elif self._db:
                for result in process_result:
                    created_by = self._get_created_by(body)
                    await self._db.save(result, created_by)
            else:
                return process_result
        except Exception as cause:
            if self.dlx:
                await self.dlx.send_event(cause, body, envelope, properties)
            logging.error(cause)

    async def _execute(self, data: bytes) -> Any:
        logging.info(f"Initializing event processing...")
        result = await self.task.execute(data)
        logging.info(f"Event successfully processed.")
        return result

    def _get_created_by(self, payload: bytes) -> str:
        raw_data = json.loads(payload)
        return str(raw_data.get("createdBy", "anonymous"))

    async def reject_event(self, envelope: Envelope, requeue: bool = False) -> None:
        await self.client.channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag, requeue=requeue
        )

    async def ack_event(self, envelope: Envelope) -> None:
        await self.client.channel.basic_client_ack(delivery_tag=envelope.delivery_tag)
