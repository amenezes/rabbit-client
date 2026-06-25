import aio_pika
from aio_pika.abc import AbstractChannel
from attrs import field, mutable

from rabbit.exceptions import ClientNotConnectedError, ExchangeNotFound
from rabbit.logger import logger


@mutable(repr=False)
class Publish:
    _channel: AbstractChannel | None = field(default=None, init=False)

    def __repr__(self) -> str:
        return "Publish()"

    @property
    def channel(self) -> AbstractChannel:
        if self._channel is None:
            raise ClientNotConnectedError
        return self._channel

    @channel.setter
    def channel(self, channel: AbstractChannel) -> None:
        self._channel = channel

    async def send_event(
        self,
        payload: bytes,
        exchange_name: str = "default.in.exchange",
        routing_key: str = "#",
        **kwargs,
    ) -> None:
        try:
            exchange = await self.channel.declare_exchange(
                exchange_name,
                passive=True,
            )
            await exchange.publish(
                aio_pika.Message(payload, **kwargs),
                routing_key=routing_key,
            )
        except aio_pika.exceptions.ChannelNotFoundEntity as err:
            raise ExchangeNotFound(exchange_name) from err
        except Exception as err:
            logger.error(f"Failed to publish to '{exchange_name}': {err}")
            raise
