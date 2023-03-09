import asyncio

from rich.progress import track

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


class Publisher:
    def __init__(self, exchange_name: str, routing_key: str, **kwargs):
        self.loop = asyncio.get_event_loop()
        self.client = AioRabbitClient()
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.loop.run_until_complete(self.client.connect(**kwargs))
        self.publish = self.configure_publish()

    def configure_publish(self) -> Publish:
        publish = Publish()
        self.loop.run_until_complete(self.client.register(publish))
        return publish

    def send_event(self, payload: bytes, qtd: int, name: str) -> None:
        for _ in track(range(0, qtd), description=f"📤 Sending '{name}':"):
            self.loop.run_until_complete(
                self.publish.send_event(payload, self.exchange_name, self.routing_key)
            )
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
