from typing import Any

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection


class AioRabbitClient:
    """Async RabbitMQ client with automatic connection recovery.

    Powered by aio-pika / aiormq — reconnection, channel recovery, and
    topology restoration are handled natively by ``connect_robust``.
    """

    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None

    async def connect(self, url: str = "", **kwargs: Any) -> None:
        """Connect to the RabbitMQ broker.

        Accepts either a full AMQP URL or keyword arguments
        (host, port, login, password, virtualhost, etc.).
        """
        if url:
            self._connection = await aio_pika.connect_robust(url, **kwargs)
        else:
            self._connection = await aio_pika.connect_robust(**kwargs)

    async def channel(self) -> AbstractChannel:
        """Return a new robust channel from the current connection."""
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return await self._connection.channel()

    async def close(self) -> None:
        """Close the connection gracefully."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    @property
    def is_connected(self) -> bool:
        """Check whether the client has an active connection."""
        return self._connection is not None and not self._connection.is_closed

    async def __aenter__(self) -> "AioRabbitClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
