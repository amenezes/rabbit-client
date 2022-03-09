import pytest

from rabbit.client import AioRabbitClient
from rabbit.exceptions import AttributeNotInitialized
from rabbit.job import async_echo_job
from rabbit.subscribe import Subscribe
from tests.conftest import ChannelMock, EnvelopeMock, PropertiesMock

PAYLOAD = b'{"a": 1}'


@pytest.mark.asyncio
async def test_configure(subscribe_mock):
    await subscribe_mock.configure()


@pytest.mark.asyncio
async def test_configure_with_client_not_initialized():
    subscribe = Subscribe(AioRabbitClient(), async_echo_job)
    with pytest.raises(AttributeNotInitialized):
        await subscribe.configure()


@pytest.mark.asyncio
async def test_configure_with_dlx(subscribe_dlx):
    await subscribe_dlx.configure()


@pytest.mark.asyncio
async def test_reject_event(subscribe_mock):
    await subscribe_mock.configure()
    await subscribe_mock.reject_event(EnvelopeMock())


@pytest.mark.asyncio
async def test_ack_event(subscribe_mock):
    await subscribe_mock.configure()
    await subscribe_mock.ack_event(EnvelopeMock())


def test_subscribe_with_dlx(dlx, subscribe_dlx):
    assert subscribe_dlx._dlx is not None


@pytest.mark.asyncio
async def test_callback(subscribe_mock):
    await subscribe_mock.configure()
    result = await subscribe_mock.callback(
        ChannelMock(), b'{"key": "value"}', EnvelopeMock(), PropertiesMock()
    )
    assert result is None


def test_subscribe_repr(subscribe_mock):
    assert isinstance(repr(subscribe_mock), str)
