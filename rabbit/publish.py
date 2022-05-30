import asyncio
import os
from typing import Optional

from attrs import field, mutable, validators

from .client import AioRabbitClient


@mutable(repr=False)
class Publish:
    _client: AioRabbitClient = field(
        validator=validators.instance_of(AioRabbitClient),
    )
    _channel = field(init=False)

    def __repr__(self) -> str:
        return f"Publish(channel_id={self.channel_id}, publisher_confirms={self.publisher_confirms})"

    @property
    def publisher_confirms(self) -> bool:
        try:
            return self._channel.publisher_confirms  # type: ignore
        except AttributeError:
            return False

    @property
    def channel_id(self) -> int:
        try:
            return self._channel.channel_id  # type: ignore
        except AttributeError:
            return 0

    async def configure(self) -> None:
        await asyncio.sleep(1.5)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        loop.create_task(self._client.watch(self), name="publish_watcher")

    async def enable_publish_confirms(self) -> None:
        try:
            if not self._channel.publisher_confirms:
                await self._channel.confirm_select()
        except AttributeError:
            self._channel = await self._client.get_channel()
            await self.enable_publish_confirms()

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
