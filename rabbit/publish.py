import asyncio
import os

import attr

from rabbit.client import AioRabbitClient


@attr.s(slots=True)
class Publish:
    _client = attr.ib(
        type=AioRabbitClient,
        validator=attr.validators.instance_of(AioRabbitClient),
        repr=False,
    )
    exchange_name = attr.ib(
        type=str,
        default=os.getenv("PUBLISH_EXCHANGE_NAME", "default.in.exchange"),
        validator=attr.validators.instance_of(str),
    )
    routing_key = attr.ib(
        type=str,
        default=os.getenv("PUBLISH_ROUTING_KEY", "#"),
        validator=attr.validators.instance_of(str),
    )
    _channel = attr.ib(init=False, repr=False)

    async def configure(self) -> None:
        await asyncio.sleep(1)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        # loop.create_task(self._client.watch(self), name="publish_watcher")
        loop.create_task(self._client.watch(self))

    async def send_event(self, payload: bytes, **kwargs) -> None:
        await self._channel.publish(
            payload=payload,
            exchange_name=self.exchange_name,
            routing_key=self.routing_key,
            **kwargs,
        )
