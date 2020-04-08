import asyncio

import pytest

from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

from rabbit import async_echo_job, echo_job
from rabbit.client import AioRabbitClient
from rabbit.subscribe import Subscribe
from rabbit.publish import Publish
from rabbit.queue import Queue
from rabbit.observer import Observer
from rabbit.polling import PollingPublisher
from rabbit.exchange import Exchange
from rabbit.tlog.db import DB
from rabbit.tlog.migration import Migration
from rabbit.dlx import DLX
from rabbit.tlog import Event
from rabbit.task import ProcessTask, StandardTask


class AioRabbitClientMock(AioRabbitClient):
    def __init__(self, *args, **kwargs):
        self.protocol = ProtocolMock()
        self.transport = TransportMock()
        self._channel = ChannelMock()
        self._observer = Observer()
        self._app = kwargs.get('app')

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        pass


class ChannelMock:
    def __init__(self):
        self.channel = 'channel'

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


class TransportMock:
    def __init__(self):
        self.transport = 'transport'

    def close(self):
        pass


class ProtocolMock:
    def __init__(self):
        self.protocol = 'protocol'

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


class DBMock(DB):
    def __init__(self, value=False):
        self.value = value

    async def exec(self, stmt, params={}):
        pass

    async def get_oldest_event(self):
        if self.value:
            return Event(body=b"test")


class MigrationMock(Migration):
    pass


class PropertiesMock(Properties):

    def __init__(self, headers={'x-delay': 5000}):
        self.headers = headers


class EnvelopeMock(Envelope):

    def __init__(self):
        pass

    @property
    def exchange_name(self):
        return 'src-exchange'

    @property
    def routing_key(self):
        return '#'

    @property
    def delivery_tag(self):
        return True


@pytest.mark.asyncio
@pytest.fixture
async def loop():
    try:
        loop = asyncio.get_running_loop()
    except AttributeError:
        loop = asyncio._get_running_loop()
    return loop


# @pytest.fixture
# def subscribe_mock():
#     return SubscribeMock()


@pytest.fixture
def client():
    return AioRabbitClient()


@pytest.fixture
async def subscribe(client):
    return Subscribe(client=client)


@pytest.fixture
async def subscribe_with_process_job(client):
    return Subscribe(client=client, task=ProcessTask())


@pytest.fixture
async def subscribe_with_standard_job(client):
    return Subscribe(client=client, task=StandardTask())


@pytest.fixture
async def process_task():
    return ProcessTask(job=async_echo_job)


@pytest.fixture
async def standard_task():
    return StandardTask(job=echo_job)


@pytest.fixture
def queue():
    return Queue(name="queue")


@pytest.fixture
def publish(client):
    return Publish(client=client)


@pytest.fixture
def observer():
    return Observer()


@pytest.fixture
def exchange():
    return Exchange(name="exchange", exchange_type="topic", topic="#")


# @pytest.fixture
# def db():
#     return DB(migration=MigrationMock())


@pytest.fixture
def polling_mock(publish_mock):
    return PollingPublisher(publish_mock, DBMock())


@pytest.fixture
def dlx(client):
    return DLX(client)


@pytest.fixture
@pytest.mark.asyncio
async def publish_mock(loop):
    return Publish(AioRabbitClientMock(app=loop))


@pytest.fixture
def subscribe_mock():
    return Subscribe(
        client=AioRabbitClientMock(),
        task=StandardTask()
    )


@pytest.fixture
def subscribe_dlx(dlx):
    return Subscribe(
        client=AioRabbitClientMock(),
        task=StandardTask(),
        dlx=dlx
    )

@pytest.fixture
def subscribe_all(dlx, publish_mock):
    return Subscribe(
        client=AioRabbitClientMock(),
        task=StandardTask(),
        dlx=dlx,
        publish=publish_mock
    )
