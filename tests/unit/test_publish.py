import pytest
from aioamqp.exceptions import ChannelClosed

from rabbit import Publish
from rabbit.exceptions import ClientNotConnectedError, ExchangeNotFound


def test_register_publish_without_client_connected(publish):
    with pytest.raises(ClientNotConnectedError):
        _ = publish.channel


def test_publish_repr(publish_mock):
    assert repr(publish_mock) == "Publish(channel_id=0, publisher_confirms=False)"


async def test_publish_confirms_disabled(publish):
    assert publish.publish_confirms is False


async def test_publish_confirms_enabled():
    publish = Publish(True)
    assert publish.publish_confirms is True


async def test_send_event_channel_closed_propagates(publish_mock):
    async def _raise(*args, **kwargs):
        raise ChannelClosed("PRECONDITION_FAILED - channel closed")

    publish_mock.channel.publish = _raise

    with pytest.raises(ChannelClosed):
        await publish_mock.send_event(b"test")


async def test_send_event_exchange_not_found(publish_mock):
    async def raise_no_exchange(*args, **kwargs):
        raise ChannelClosed("PRECONDITION_FAILED - no exchange 'test-exchange'")

    publish_mock.channel.publish = raise_no_exchange

    with pytest.raises(ExchangeNotFound) as exc_info:
        await publish_mock.send_event(b"test")

    assert "default.in.exchange" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ChannelClosed)


@pytest.mark.parametrize(
    "attribute", ["publish_confirms", "name", "channel_id", "channel"]
)
def test_publish_attributes(attribute):
    assert hasattr(Publish, attribute)
