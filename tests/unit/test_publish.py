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


def test_publish_repr(publish):
    assert repr(publish) == "Publish(channel_id=0, publisher_confirms=False)"


@pytest.mark.asyncio
async def test_enable_publish_confirms(publish_mock):
    assert publish_mock.publisher_confirms is False
    await publish_mock.enable_publish_confirms()
    assert publish_mock.publisher_confirms is True


@pytest.mark.asyncio
async def test_enable_publish_confirms_twice(publish_mock):
    assert publish_mock.publisher_confirms is False
    await publish_mock.enable_publish_confirms()
    await publish_mock.enable_publish_confirms()
    assert publish_mock.publisher_confirms is True
