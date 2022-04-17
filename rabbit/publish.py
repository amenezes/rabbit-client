import asyncio
import os

from attrs import field, mutable, validators

from .client import AioRabbitClient


@mutable
class Publish:
    _client: AioRabbitClient = field(
        validator=validators.instance_of(AioRabbitClient),
        repr=False,
    )
    exchange_name: str = field(
        default=os.getenv("PUBLISH_EXCHANGE_NAME", "default.in.exchange"),
        validator=validators.instance_of(str),
    )
    routing_key: str = field(
        default=os.getenv("PUBLISH_ROUTING_KEY", "#"),
        validator=validators.instance_of(str),
    )
    _channel = field(init=False, repr=False)

    async def configure(self) -> None:
        await asyncio.sleep(1)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        loop.create_task(self._client.watch(self), name="publish_watcher")

    async def send_event(self, payload: bytes, **kwargs) -> None:
        await self._channel.publish(
            payload=payload,
            exchange_name=self.exchange_name,
            routing_key=self.routing_key,
            **kwargs,
        )
