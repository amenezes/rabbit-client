import asyncio
import os
from typing import Optional

from attrs import field, mutable, validators

from .client import AioRabbitClient


@mutable
class Publish:
    _client: AioRabbitClient = field(
        validator=validators.instance_of(AioRabbitClient),
        repr=False,
    )
    _channel = field(init=False, repr=False)

    async def configure(self) -> None:
        await asyncio.sleep(1)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        loop.create_task(self._client.watch(self), name="publish_watcher")

    async def send_event(
        self,
        payload: bytes,
        exchange_name: Optional[str] = None,
        routing_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        exchange_name = exchange_name or os.getenv(
            "PUBLISH_EXCHANGE_NAME", "default.in.exchange"
        )
        routing_key = routing_key or os.getenv("PUBLISH_ROUTING_KEY", "#")
        await self._channel.publish(
            payload=payload,
            exchange_name=exchange_name,
            routing_key=routing_key,
            **kwargs,
        )
