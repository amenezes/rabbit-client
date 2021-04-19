import pytest

from rabbit.client import aioamqp
from rabbit.exceptions import AttributeNotInitialized
from tests.conftest import AioAmqpMock


async def aioamqp_mock(*args, **kwargs):
    aioamqp_mock = AioAmqpMock()
    transport, protocol = await aioamqp_mock.connect(args, kwargs)
    return transport, protocol


@pytest.mark.asyncio
async def test_connect(client, monkeypatch):
    monkeypatch.setattr(aioamqp, "connect", aioamqp_mock)
    await client.connect()
    channel = await client.get_channel()
    assert channel is not None


@pytest.mark.skip
async def test_persistent_connect(client, monkeypatch):
    monkeypatch.setattr(aioamqp, "connect", aioamqp_mock)
    await client.persistent_connect()


@pytest.mark.asyncio
async def test_channel_not_initialized(client):
    with pytest.raises(AttributeNotInitialized):
        await client.get_channel()
