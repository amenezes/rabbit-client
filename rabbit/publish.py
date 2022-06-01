import asyncio
import os
from typing import Optional

from aioamqp.exceptions import ChannelClosed
from attrs import field, mutable, validators

from .client import AioRabbitClient
from .exceptions import ExchangeNotFound


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
        """Check if publisher_confirms was enable on the channel."""
        try:
            return self._channel.publisher_confirms  # type: ignore
        except AttributeError:
            return False

    @property
    def channel_id(self) -> int:
        """Check the current channel ID."""
        try:
            return self._channel.channel_id  # type: ignore
        except AttributeError:
            return 0

    async def configure(self, enable_publish_confirms: bool = False) -> None:
        """Configure publisher channel."""
        await asyncio.sleep(1.5)
        self._channel = await self._client.get_channel()
        loop = asyncio.get_running_loop()
        loop.create_task(self._client.watch(self), name="publish_watcher")
        if enable_publish_confirms:
            await self.enable_publish_confirms()

    async def enable_publish_confirms(self) -> None:
        """Enables publish_confirms resource on the publisher channel."""
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
        """Sends event message to broker."""
        exchange_name = exchange_name or os.getenv(
            "PUBLISH_EXCHANGE_NAME", "default.in.exchange"
        )
        routing_key = routing_key or os.getenv("PUBLISH_ROUTING_KEY", "#")
        try:
            await self._channel.publish(
                payload=payload,
                exchange_name=exchange_name,
                routing_key=routing_key,
                **kwargs,
            )
        except ChannelClosed as err:
            await self.configure(enable_publish_confirms=self.publisher_confirms)
            if err.message.find("no exchange") > 0:
                raise ExchangeNotFound(f"Exchange '{exchange_name}' not found")
