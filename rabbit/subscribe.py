import asyncio
import logging
import os
from typing import List, Optional

from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.exceptions import SynchronizationError
from aioamqp.properties import Properties

import attr

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exceptions import AttributeNotInitialized
from rabbit.exchange import Exchange
from rabbit.job import echo_job
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.task import Task


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class Subscribe:

    client = attr.ib(
        type=AioRabbitClient,
        validator=attr.validators.instance_of(AioRabbitClient)
    )
    exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange'),
            exchange_type=os.getenv('SUBSCRIBE_EXCHANGE_TYPE', 'topic'),
            topic=os.getenv('SUBSCRIBE_TOPIC', '#')
        ),
        validator=attr.validators.instance_of(Exchange)
    )
    queue = attr.ib(
        type=Queue,
        default=Queue(
            name=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')
        ),
        validator=attr.validators.instance_of(Queue)
    )
    dlx = attr.ib(
        type=DLX,
        default=DLX(
            dlq_queue=Queue(
                name=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue'),
                arguments={
                    'x-dead-letter-exchange': os.getenv(
                        'SUBSCRIBE_EXCHANGE', 'default.in.exchange'
                    ),
                    'x-dead-letter-routing-key': os.getenv(
                        'SUBSCRIBE_TOPIC', '#'
                    )
                }
            ),
            routing_key=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')
        ),
        validator=attr.validators.instance_of(DLX)
    )
    task = attr.ib(
        type=Task,
        default=Task(
            job=echo_job
        ),
        validator=attr.validators.instance_of(Task)
    )
    task_type = attr.ib(
        default='standard',
        validator=attr.validators.and_(
            attr.validators.in_(['standard', 'process']),
            attr.validators.instance_of(str)
        )
    )
    _publish = attr.ib(
        type=Optional[Publish],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Publish)
        )
    )

    def __attrs_post_init__(self) -> None:
        self.client.monitor_connection(self)
        self.dlx.client = self.client
        if self.publish:
            self.publish.client = self.client

    @property
    def publish(self) -> Optional[Publish]:
        return self._publish

    @publish.setter
    def publish(self, publish: Publish) -> None:
        if not isinstance(publish, Publish):
            raise ValueError('publish must be Publish instance.')
        logging.info('Registering connection monitoring')
        self._publish = publish
        self._publish.client = self.client

    async def configure(self) -> None:
        await asyncio.sleep(5)
        try:
            await self._configure_exchange()
            await self._configure_queue()
            await self.dlx.configure()
            await self._configure_publish()
            await self._configure_queue_bind()
        except AttributeNotInitialized:
            logging.debug('Waiting client initialization...SUBSCRIBE')
        except SynchronizationError:
            pass

    async def _configure_publish(self) -> None:
        if self.publish:
            await self.publish.configure()

    async def _configure_exchange(self) -> None:
        await self.client.channel.exchange_declare(
            exchange_name=self.exchange.name,
            type_name=self.exchange.exchange_type,
            durable=self.exchange.durable
        )
        await asyncio.sleep(5)

    async def _configure_queue(self) -> None:
        await self.client.channel.queue_declare(
            queue_name=self.queue.name,
            durable=self.queue.durable
        )

    async def _configure_queue_bind(self) -> None:
        await self.client.channel.queue_bind(
            exchange_name=self.exchange.name,
            queue_name=self.queue.name,
            routing_key=self.exchange.topic
        )
        await self.client.channel.basic_consume(
            callback=self.callback,
            queue_name=self.queue.name
        )

    async def _execute(self, data: bytes) -> List[bytes]:
        process_result = [bytes()]
        if self.task_type == 'process':
            process_result = await self.task.process_executor(data)
            return process_result
        # else:
        process_result = await self.task.std_executor(data)
        return process_result

    async def callback(self,
                       channel: Channel,
                       body: bytes,
                       envelope: Envelope,
                       properties: Properties):
        try:
            process_result = await self._execute(body)
            await self.ack_event(envelope)

            if self.publish:
                for result in process_result:
                    await self.publish.send_event(result)
            else:
                return process_result
        except Exception as cause:
            await self.dlx.send_event(cause, body, envelope, properties)
            await self.reject_event(envelope)

    async def reject_event(self, envelope: Envelope, requeue: bool = False) -> None:
        await self.client.channel.basic_client_nack(
            delivery_tag=envelope.delivery_tag,
            requeue=requeue
        )

    async def ack_event(self, envelope: Envelope) -> None:
        await self.client.channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag
        )
