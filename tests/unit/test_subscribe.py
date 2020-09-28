import pytest

from conftest import ChannelMock, EnvelopeMock, PropertiesMock

PAYLOAD = b'{"a": 1}'


@pytest.mark.asyncio
async def test_configure(subscribe_mock):
    await subscribe_mock.configure()


@pytest.mark.asyncio
async def test_configure_with_dlx(subscribe_dlx):
    await subscribe_dlx.configure()


@pytest.mark.asyncio
async def test_configure_publish(subscribe_all):
    await subscribe_all._configure_publish()


@pytest.mark.asyncio
async def test_configure_exchange(subscribe_mock):
    await subscribe_mock._configure_exchange()


@pytest.mark.asyncio
async def test_configure_queue(subscribe_mock):
    await subscribe_mock._configure_queue()


@pytest.mark.asyncio
async def test_configure_queue_bind(subscribe_mock):
    await subscribe_mock._configure_queue_bind()


def test_get_created_by(subscribe_mock):
    result = subscribe_mock._get_created_by(b'{"key": "value"}')
    assert result is not None


@pytest.mark.asyncio
async def test_reject_event(subscribe_mock):
    await subscribe_mock.reject_event(EnvelopeMock())


@pytest.mark.asyncio
async def test_ack_event(subscribe_mock):
    await subscribe_mock.ack_event(EnvelopeMock())


def test_subscribe_with_dlx(dlx, subscribe_dlx):
    assert subscribe_dlx.dlx is not None


@pytest.mark.asyncio
async def test_callback(subscribe_mock):
    result = await subscribe_mock.callback(
        ChannelMock(), b'{"key": "value"}', EnvelopeMock(), PropertiesMock()
    )
    assert result == b'{"key": "value"}'


@pytest.mark.asyncio
async def test_callback_with_publish(subscribe_all):
    result = await subscribe_all.callback(
        ChannelMock(), b'{"key": "value"}', EnvelopeMock(), PropertiesMock()
    )
    assert result == b'{"key": "value"}'
