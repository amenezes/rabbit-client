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


# @pytest.mark.asyncio
# async def test_callback_with_publish(subscribe_all):
#     result = await subscribe_all.callback(
#         ChannelMock(), b'{"key": "value"}', EnvelopeMock(), PropertiesMock()
#     )
#     assert result is None
