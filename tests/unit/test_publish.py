import pytest

from rabbit.exceptions import AttributeNotInitialized


@pytest.mark.asyncio
async def test_configure(publish_mock):
    await publish_mock.configure()


@pytest.mark.asyncio
async def test_configure_with_client_not_initialized(publish):
    with pytest.raises(AttributeNotInitialized):
        await publish.configure()


@pytest.mark.asyncio
async def test_send_event(publish_mock):
    await publish_mock.configure()
    await publish_mock.send_event(123)
