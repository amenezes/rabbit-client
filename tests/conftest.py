from contextlib import asynccontextmanager
from typing import Any, Callable

import pytest

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exchange import Exchange
from rabbit.job import async_echo_job
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.subscribe import Subscribe


class MockExchange:
    def __init__(self, name: str = "mock-exchange", exchange_type: str = "direct"):
        self.name = name
        self.exchange_type = exchange_type
        self.publish_calls: list[tuple[Any, str]] = []

    async def publish(self, message: Any, routing_key: str = "") -> None:
        self.publish_calls.append((message, routing_key))

    async def bind(self, exchange: "MockExchange", routing_key: str = "") -> None:
        pass


class MockQueue:
    def __init__(self, name: str = "mock-queue"):
        self.name = name
        self.consume_callback: Callable | None = None
        self.bind_calls: list[tuple[Any, str]] = []

    async def bind(self, exchange: Any, routing_key: str = "") -> None:
        self.bind_calls.append((exchange, routing_key))

    async def consume(self, callback: Callable) -> None:
        self.consume_callback = callback


class MockChannel:
    def __init__(self):
        self.is_closed = False
        self.publisher_confirms = False
        self.qos_prefetch: int | None = None
        self.exchanges: dict[str, MockExchange] = {}
        self.queues: dict[str, MockQueue] = {}

    async def set_qos(self, prefetch_count: int = 0, prefetch_size: int = 0) -> None:
        self.qos_prefetch = prefetch_count

    async def declare_exchange(
        self,
        name: str,
        exchange_type: Any = None,
        durable: bool = True,
        passive: bool = False,
    ) -> MockExchange:
        if name not in self.exchanges:
            self.exchanges[name] = MockExchange(name)
        return self.exchanges[name]

    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        arguments: dict | None = None,
        passive: bool = False,
    ) -> MockQueue:
        if name not in self.queues:
            self.queues[name] = MockQueue(name)
        return self.queues[name]

    async def close(self) -> None:
        self.is_closed = True


class MockMessage:
    def __init__(
        self,
        body: bytes = b"",
        headers: dict | None = None,
        exchange: str = "",
        routing_key: str = "",
        delivery_tag: int = 1,
    ):
        self.body = body
        self.headers = headers or {}
        self.exchange = exchange
        self.routing_key = routing_key
        self.delivery_tag = delivery_tag
        self.acked = False
        self.nacked = False
        self.rejected = False

    async def ack(self) -> None:
        self.acked = True

    async def nack(self, requeue: bool = True) -> None:
        self.nacked = True

    async def reject(self, requeue: bool = False) -> None:
        self.rejected = True

    @asynccontextmanager
    async def process(
        self,
        requeue: bool = False,
        reject_on_redelivered: bool = False,
        ignore_processed: bool = False,
    ):
        try:
            yield self
        except Exception:
            if not ignore_processed and not self.acked:
                await self.reject(requeue=requeue)
            raise


class AioRabbitClientMock(AioRabbitClient):
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def connect(self, *args, **kwargs):
        pass

    async def channel(self):
        return MockChannel()


@pytest.fixture
async def client():
    return AioRabbitClient()


@pytest.fixture
async def client_mock():
    return AioRabbitClientMock()


@pytest.fixture
async def subscribe():
    return Subscribe(task=async_echo_job)


@pytest.fixture
async def subscribe_mock(subscribe):
    subscribe.channel = MockChannel()
    return subscribe


@pytest.fixture
async def publish():
    return Publish()


@pytest.fixture
async def publish_mock(publish):
    publish.channel = MockChannel()
    return publish


@pytest.fixture
async def dlx():
    return DLX(
        Exchange(name="dlx", exchange_type="direct"),
        Exchange(name="dlq_rerouter", exchange_type="topic", topic="queue"),
        Queue(
            name="queue",
            arguments={
                "x-dead-letter-exchange": "dlq_rerouter",
                "x-dead-letter-routing-key": "queue",
            },
        ),
    )


@pytest.fixture
async def dlx_mock():
    return DLX(
        Exchange(name="dlx", exchange_type="direct"),
        Exchange(name="dlq_rerouter", exchange_type="topic", topic="queue"),
        Queue(
            name="queue",
            arguments={
                "x-dead-letter-exchange": "dlq_rerouter",
                "x-dead-letter-routing-key": "queue",
            },
        ),
    )


@pytest.fixture(scope="session")
def queue():
    return Queue(name="queue")


@pytest.fixture
def exchange():
    return Exchange(name="exchange", exchange_type="topic", topic="#")


@pytest.fixture
def mock_message():
    return MockMessage(body=b'{"key": "value"}', headers={"x-delay": 5000})


@pytest.fixture
def mock_channel():
    return MockChannel()
