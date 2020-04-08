import pytest

from conftest import AioAmqpMock
from rabbit import AttributeNotInitialized
from rabbit.client import aioamqp


async def aioamqp_mock(*args, **kwargs):
    aioamqp_mock = AioAmqpMock()
    transport, protocol = await aioamqp_mock.connect(args, kwargs)
    return transport, protocol


def test_watch(client, subscribe_mock):
    client.watch(subscribe_mock)
    assert subscribe_mock in client._observer.observers


@pytest.mark.asyncio
async def test_connect(client, monkeypatch):
    monkeypatch.setattr(aioamqp, "connect", aioamqp_mock)
    await client.connect()
    assert client.channel is not None


@pytest.mark.skip
async def test_persistent_connect(client, monkeypatch):
    monkeypatch.setattr(aioamqp, "connect", aioamqp_mock)
    await client.persistent_connect()


def test_channel_not_initialized(client):
    with pytest.raises(AttributeNotInitialized):
        client.channel
