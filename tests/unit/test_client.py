import asyncio

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


@pytest.mark.asyncio
async def test_channel_not_initialized(client):
    with pytest.raises(AttributeNotInitialized):
        await client.get_channel()


@pytest.mark.asyncio
async def test_watch(client):
    loop = asyncio.get_running_loop()
    loop.create_task(client.watch(client))
    client.protocol = "xxx"
