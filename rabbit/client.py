import asyncio
import logging

from aioamqp.channel import Channel

import attr

from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.dlx import DLX


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitClient:

    channel = attr.ib(
        type=Channel
    )
    publish = attr.ib(
        type=Publish,
        default=Publish(),
        validator=attr.validators.instance_of(Publish)
    )
    subscribe = attr.ib(
        type=Subscribe,
        default=Subscribe(),
        validator=attr.validators.instance_of(Subscribe)
    )
    dlx = attr.ib(
        type=DLX,
        default=DLX(),
        validator=attr.validators.instance_of(DLX)
    )

    def __attrs_post_init__(self):
        self.publish.channel = self.channel
        self.subscribe.channel = self.channel
        self.dlx.channel = self.channel

    async def configure(self):
        logging.info('Configurando o message broker...')
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_bind()
        logging.info('Successfully.')

    async def configure_exchange(self):
        logging.info('Configurando as exchanges...')
        await self.subscribe.configure_exchange()
        await self.publish.configure_exchange()
        await self.dlx.configure_exchange()
        await asyncio.sleep(2)

    async def configure_queue(self):
        logging.info('Configurando as queues...')
        await self.subscribe.configure_queue()
        await self.publish.configure_queue()
        await self.dlx.configure_queue()

    async def configure_bind(self):
        logging.info('Configurando o binding das queues...')
        await self.subscribe.configure_queue_bind()
        await self.publish.configure_queue_bind()
        await self.dlx.configure_queue_bind()
