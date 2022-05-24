import asyncio

from tqdm import tqdm

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


class Producer:
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
        tasks = []
        with tqdm(total=self.qtd, unit="event", desc="events") as pbar:
            pbar.set_description("sending events...")
            for i in range(0, self.qtd):
                task = self.loop.create_task(
                    publish.send_event(
                        self.payload, self.exchange_name, self.routing_key
                    )
                )
                tasks.append(task)
                pbar.update(1)
            self.loop.run_until_complete(asyncio.gather(*tasks))
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
