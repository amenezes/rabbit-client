import asyncio
import logging

import attr

from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.queues import Queues
from rabbit.exchanges import Exchanges


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class AioRabbitClient:

    _channel = attr.ib(default=None)
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

    def __attrs_post_init__(self):
        if not self._channel:
            self._channel = aioAmqp.channel

    async def configure(self):
        logging.info('Configurando o message broker...')
        await self.configure_exchange()
        await self.configure_queue()
        await self.configure_bind()
        logging.info('Successfully.')

    async def configure_exchange(self):
        logging.info('Configurando as exchanges...')
        await self.subscribe.configure_exchange(self._channel)
        await self.publish.configure_exchange(self._channel)
        await asyncio.sleep(2)

    async def configure_queue(self):
        logging.info('Configurando as queues...')
        await self.subscribe.configure_queue()
        await self.publish.configure_queue()

    async def configure_bind(self):
        logging.info('Configurando o binding das queues...')
        await self.subscribe.configure_queue_bind()
        await self.publish.configure_queue_bind()
