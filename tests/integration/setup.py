import os

from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.subscribe import Subscribe


class EnvelopeMock(Envelope):

    def __init__(self):
        pass

    @property
    def exchange_name(self):
        return 'src-exchange'

    @property
    def routing_key(self):
        return '#'
    
    @property
    def delivery_tag(self):
        return True     


class PropertiesMock(Properties):

    def __init__(self, headers={'x-delay': 5000}):
        self.headers = headers


async def rabbit_client(loop):
    client = AioRabbitClient(app=loop)
    await client.connect()
    return client


async def get_publish(client=None):
    return Publish(client)


async def get_subscribe(client=None):
    return Subscribe(client)


async def get_dlx(client=None):
    return DLX(
        client=client,
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
    )