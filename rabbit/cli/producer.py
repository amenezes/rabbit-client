import asyncio

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.publish import Publish


class Producer:
    def __init__(
        self,
        payload: bytes,
        qtd: int,
        name: str,
        exchange_type: str,
        topic: str,
    ):
        self.loop = asyncio.get_event_loop()
        self.client = AioRabbitClient()
        self.qtd = qtd
        self.payload = payload
        self.name = name
        self.exchange_type = exchange_type
        self.topic = topic
        self.loop.run_until_complete(self.client.connect())

    def configure_publish(self):
        publish = Publish(
            self.client,
            exchange=Exchange(
                name=self.name,
                topic=self.topic,
                exchange_type=self.exchange_type,
            ),
        )
        self.loop.run_until_complete(publish.configure())
        return publish

    def send_event(self):
        publish = self.configure_publish()
        tasks = []
        for i in range(0, self.qtd):
            task = self.loop.create_task(publish.send_event(self.payload))
            tasks.append(task)
        self.loop.run_until_complete(asyncio.gather(*tasks))
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
