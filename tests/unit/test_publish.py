import pytest

from rabbit.exceptions import ClientNotConnectedError


async def test_send_event(publish_mock):
    await publish_mock.send_event(123)


async def test_register_publish_without_client_connected(publish):
    with pytest.raises(ClientNotConnectedError):
        await publish.configure(True)


def test_publish_repr(publish_mock):
    assert repr(publish_mock) == "Publish(channel_id=0, publisher_confirms=False)"


async def test_enable_publish_confirms(publish_mock):
    assert publish_mock.publisher_confirms is False
    await publish_mock.enable_publish_confirms()
    assert publish_mock.publisher_confirms is True


async def test_enable_publish_confirms_twice(publish_mock):
    assert publish_mock.publisher_confirms is False
    await publish_mock.enable_publish_confirms()
    await publish_mock.enable_publish_confirms()
    assert publish_mock.publisher_confirms is True
