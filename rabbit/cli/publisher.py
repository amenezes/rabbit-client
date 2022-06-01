import asyncio

from rich.progress import track

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


class Publisher:
    def __init__(
        self, payload: bytes, qtd: int, exchange_name: str, routing_key: str, **kwargs
    ):
        self.loop = asyncio.get_event_loop()
        self.client = AioRabbitClient()
        self.qtd = qtd
        self.payload = payload
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.loop.run_until_complete(self.client.connect(**kwargs))

    def configure_publish(self):
        publish = Publish(self.client)
        self.loop.run_until_complete(publish.configure())
        return publish

    def send_event(self):
        publish = self.configure_publish()
        for i in track(range(0, self.qtd), description="Sending events"):
            self.loop.run_until_complete(
                publish.send_event(self.payload, self.exchange_name, self.routing_key)
            )
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
