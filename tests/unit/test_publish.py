import pytest


@pytest.mark.asyncio
async def test_configure(publish_mock):
    await publish_mock.configure()


@pytest.mark.asyncio
async def test_configure_exchange(publish_mock):
    await publish_mock._configure_exchange()


@pytest.mark.asyncio
async def test_configure_queue(publish_mock):
    await publish_mock._configure_queue()


@pytest.mark.asyncio
async def test_configure_queue_bind(publish_mock):
    await publish_mock._configure_queue_bind()


@pytest.mark.asyncio
async def test_send_event(publish_mock):
    await publish_mock.send_event(123)
