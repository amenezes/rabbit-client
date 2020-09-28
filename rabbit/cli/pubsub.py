import asyncio
import logging

from rabbit.client import AioRabbitClient
from rabbit.job import async_echo_job
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.tlog.db import DB


class PubSub:
    def __init__(self, loop=None):
        logging.getLogger().setLevel(logging.DEBUG)
        self.loop = loop or asyncio.get_event_loop()

    def init_consumer(self):
        subscribe_client = AioRabbitClient()
        self.loop.create_task(subscribe_client.persistent_connect())
        return Subscribe(client=subscribe_client, db=DB(), task=async_echo_job)

    def init_polling_publisher(self):
        polling_client = AioRabbitClient()
        self.loop.create_task(polling_client.persistent_connect())
        publish = Publish(polling_client)
        polling = PollingPublisher(publish)
        return polling, publish

    async def configure_polling_publisher(self, polling, publish, subscribe):
        await publish.configure()
        await subscribe.configure()
        await asyncio.sleep(20)
        await polling.run()

    def run(self):
        polling, publish = self.init_polling_publisher()
        subscribe = self.init_consumer()
        self.loop.run_until_complete(
            self.configure_polling_publisher(polling, publish, subscribe)
        )
        self.loop.run_forever()
