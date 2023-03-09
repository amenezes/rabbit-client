import os
from typing import Optional

from aioamqp.channel import Channel
from aioamqp.exceptions import ChannelClosed
from attrs import field, mutable

from rabbit.exceptions import ClientNotConnectedError

from .exceptions import ExchangeNotFound


@mutable(repr=False)
class Publish:
    _channel: Channel = field(init=False)

    def __repr__(self) -> str:
        return f"Publish(channel_id={self.channel_id}, publisher_confirms={self.publisher_confirms})"

    @property
    def name(self) -> str:
        return "Publish"

    @property
    def publisher_confirms(self) -> bool:
        """Check if publisher_confirms was enable on the channel."""
        try:
            return self.channel.publisher_confirms  # type: ignore
        except AttributeError:
            return False

    @property
    def channel_id(self) -> int:
        """Check the current channel ID."""
        try:
            return self.channel.channel_id  # type: ignore
        except AttributeError:
            return 0

    @property
    def channel(self) -> Channel:
        try:
            return self._channel
        except AttributeError:
            raise ClientNotConnectedError

    @channel.setter
    def channel(self, channel: Channel) -> None:
        self._channel = channel

    async def configure(self, enable_publish_confirms: bool = False) -> None:
        """Configure publisher channel."""
        if enable_publish_confirms:
            await self.enable_publish_confirms()

    async def enable_publish_confirms(self) -> None:
        """Enables publish_confirms resource on the publisher channel."""
        if self.channel:
            if not self.channel.publisher_confirms:
                await self.channel.confirm_select()

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
            await self.channel.publish(
                payload=payload,
                exchange_name=exchange_name,
                routing_key=routing_key,
                **kwargs,
            )
        except ChannelClosed as err:
            await self.configure(enable_publish_confirms=self.publisher_confirms)
            if err.message.find("no exchange") > 0:
                raise ExchangeNotFound(f"Exchange '{exchange_name}' not found")
