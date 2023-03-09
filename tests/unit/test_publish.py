import pytest

from rabbit import Publish
from rabbit.exceptions import ClientNotConnectedError


async def test_send_event(publish_mock):
    await publish_mock.send_event(123)


def test_register_publish_without_client_connected(publish):
    with pytest.raises(ClientNotConnectedError):
        hasattr(publish, "channel")


def test_publish_repr(publish_mock):
    assert repr(publish_mock) == "Publish(channel_id=0, publisher_confirms=False)"


async def test_publish_confirms_disabled(publish):
    assert publish.publish_confirms is False


async def test_publish_confirms_enabled():
    publish = Publish(True)
    assert publish.publish_confirms is True
