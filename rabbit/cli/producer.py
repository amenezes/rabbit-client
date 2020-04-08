import asyncio
import json
import os

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.publish import Publish
from rabbit.queue import Queue

PAYLOAD = json.dumps(
    {"document": 1, "description": "123", "pages": ["abc 123", "def 456", "ghi 789"]}
)


class Producer:
    def __init__(self, loop=None, client=None, qtd=1):
        self.loop = loop or asyncio.get_event_loop()
        self.client = client or AioRabbitClient()
        self.qtd = qtd
        self.loop.run_until_complete(self.client.connect())

    def configure_publish(self):
        publish = Publish(
            self.client,
            exchange=Exchange(
                name=os.getenv("SUBSCRIBE_EXCHANGE", "default.in.exchange"),
                exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", "topic"),
                topic=os.getenv("SUBSCRIBE_TOPIC", "#"),
            ),
            queue=Queue(name=os.getenv("SUBSCRIBE_QUEUE", "default.subscribe.queue")),
        )
        self.loop.run_until_complete(publish.configure())
        return publish

    def send_event(self):
        publish = self.configure_publish()
        for i in range(0, self.qtd):
            self.loop.run_until_complete(
                publish.send_event(
                    bytes(PAYLOAD, "utf-8")
                    # properties={'headers': {'x-delay': 5000}}
                )
            )
