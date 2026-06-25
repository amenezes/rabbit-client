import asyncio

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


class Publisher:
    def __init__(self, exchange_name: str, routing_key: str, **kwargs) -> None:
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.connection_kwargs = kwargs

    def send_event(self, payload: bytes, qtd: int, name: str) -> None:
        asyncio.run(self._send_batch(payload, qtd))

    async def _send_batch(self, payload: bytes, qtd: int) -> None:
        client = AioRabbitClient()
        await client.connect(**self.connection_kwargs)
        try:
            channel = await client.channel()
            publish = Publish()
            publish.channel = channel

            for _ in range(qtd):
                await publish.send_event(payload, self.exchange_name, self.routing_key)
        finally:
            await client.close()
