import asyncio
import os

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.publish import Publish


class Producer:
    def __init__(self, payload: bytes, qtd: int = 1):
        self.loop = asyncio.get_event_loop()
        self.client = AioRabbitClient()
        self.qtd = qtd
        self.payload = payload
        self.loop.run_until_complete(self.client.connect())

    def configure_publish(self):
        publish = Publish(
            self.client,
            exchange=Exchange(
                name=os.getenv("SUBSCRIBE_EXCHANGE", "default.in.exchange"),
                exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", "topic"),
                topic=os.getenv("SUBSCRIBE_TOPIC", "#"),
            ),
        )
        self.loop.run_until_complete(publish.configure())
        return publish

    def send_event(self):
        publish = self.configure_publish()
        for i in range(0, self.qtd):
            self.loop.run_until_complete(publish.send_event(self.payload))
