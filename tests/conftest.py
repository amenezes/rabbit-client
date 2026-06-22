import asyncio

import pytest
from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

from rabbit.background_tasks import BackgroundTasks
from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exchange import Exchange
from rabbit.job import async_echo_job
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.subscribe import Subscribe


class AioRabbitClientMock(AioRabbitClient):
    def __init__(self, *args, **kwargs):
        self._protocol = ProtocolMock()
        self.transport = TransportMock()
        self._app = kwargs.get("app")
        self._background_tasks = BackgroundTasks()
        self._event = asyncio.Event()
        self._items = list()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        pass

    async def get_channel(self):
        return ChannelMock()


class ChannelMock:
    def __init__(self):
        self.channel = "channel"
        self.publisher_confirms = False

    async def queue_declare(self, *args, **kwargs):
        pass

    async def exchange_declare(self, *args, **kwargs):
        pass

    async def queue_bind(self, *args, **kwargs):
        pass

    async def publish(self, *args, **kwargs):
        pass

    async def basic_consume(self, *args, **kwargs):
        pass

    async def basic_client_ack(self, *args, **kwargs):
        pass

    async def basic_client_nack(self, *args, **kwargs):
        pass

    async def basic_qos(self, *args, **kwargs):
        pass

    async def basic_reject(self, *args, **kwargs):
        pass

    async def confirm_select(self, *args, **kwargs):
        self.publisher_confirms = True


class RecordingChannelMock:
    # Detects overlapping in-flight RPCs: AMQP channels are single-threaded, so
    # concurrent RPCs (asyncio.gather) corrupt broker state. See bug-rabbit-client_8.md.
    def __init__(self):
        self.calls = []
        self.overlaps = 0
        self._in_flight = 0

    async def _rpc(self, name, key):
        self._in_flight += 1
        if self._in_flight > 1:
            self.overlaps += 1
        self.calls.append((name, key))
        await asyncio.sleep(0)
        self._in_flight -= 1

    async def basic_qos(self, **kwargs):
        await self._rpc("basic_qos", kwargs.get("prefetch_count"))

    async def queue_declare(self, **kwargs):
        await self._rpc("queue_declare", kwargs.get("queue_name"))

    async def exchange_declare(self, **kwargs):
        await self._rpc("exchange_declare", kwargs.get("exchange_name"))

    async def queue_bind(self, **kwargs):
        await self._rpc(
            "queue_bind",
            (kwargs.get("exchange_name"), kwargs.get("queue_name")),
        )

    async def basic_consume(self, **kwargs):
        await self._rpc("basic_consume", kwargs.get("queue_name"))


class TransportMock:
    def __init__(self):
        self.transport = "transport"

    def close(self):
        pass


class ProtocolMock:
    def __init__(self):
        self.protocol = "protocol"
        self.server_properties = {}

    async def channel(self):
        return SubscribeMock()

    async def wait_closed(self):
        pass


class AioAmqpMock:
    def __init__(self, *args, **kwargs):
        self.protocol = ProtocolMock()
        self.transport = TransportMock()
        self.channel = ChannelMock()

    async def connect(self, *args, **kwargs):
        return self.transport, self.protocol


class SubscribeMock:
    def __init__(self, *args, **kwargs):
        pass

    async def configure(self, *args, **kwargs):
        pass


class PropertiesMock(Properties):
    def __init__(self, headers={"x-delay": 5000}):
        self.headers = headers


class EnvelopeMock(Envelope):
    def __init__(self):
        pass

    @property
    def exchange_name(self):
        return "src-exchange"

    @property
    def routing_key(self):
        return "#"

    @property
    def delivery_tag(self):
        return True


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
async def subscribe_mock(subscribe, client_mock):
    await client_mock.register(subscribe)
    return subscribe


@pytest.fixture
async def publish():
    return Publish()


@pytest.fixture
async def publish_mock(publish, client_mock):
    await client_mock.register(publish)
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
def envelope_mock():
    return EnvelopeMock()


@pytest.fixture
def recording_channel():
    return RecordingChannelMock()


@pytest.fixture
def skip_configure_delays(monkeypatch):
    # sleep(0) MUST stay a real yield — it exposes asyncio.gather interleaving.
    # Only the >0 guard sleeps (1.5s) are skipped for speed.
    real_sleep = asyncio.sleep

    async def fast_sleep(delay, *args, **kwargs):
        if delay and delay > 0:
            return
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)
