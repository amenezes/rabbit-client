import pytest
from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

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


class TransportMock:
    def __init__(self):
        self.transport = "transport"

    def close(self):
        pass


class ProtocolMock:
    def __init__(self):
        self.protocol = "protocol"

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
def client():
    return AioRabbitClient()


@pytest.fixture
async def subscribe(client):
    return Subscribe(client=client)


@pytest.fixture
def queue():
    return Queue(name="queue")


@pytest.fixture
def publish(client):
    return Publish(client=client)


@pytest.fixture
def exchange():
    return Exchange(name="exchange", exchange_type="topic", topic="#")


@pytest.fixture
def dlx(client):
    return DLX(
        client,
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
def dlx_mock():
    return DLX(
        AioRabbitClientMock(),
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
@pytest.mark.asyncio
async def publish_mock():
    return Publish(AioRabbitClientMock())


@pytest.fixture
def subscribe_mock():
    return Subscribe(client=AioRabbitClientMock(), task=async_echo_job)


@pytest.fixture
def subscribe_dlx(dlx):
    return Subscribe(client=AioRabbitClientMock(), task=async_echo_job)


@pytest.fixture
def subscribe_all(dlx, publish_mock):
    return Subscribe(client=AioRabbitClientMock(), task=async_echo_job)
