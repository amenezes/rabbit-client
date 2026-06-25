import pytest

from rabbit.exceptions import ClientNotConnectedError, ExchangeNotFound
from rabbit.publish import Publish


def test_publish_raises_when_not_connected(publish):
    with pytest.raises(ClientNotConnectedError):
        _ = publish.channel


async def test_send_event_publishes_message(publish_mock):
    await publish_mock.send_event(b"test payload", "test-exchange", "test.key")

    exchange = publish_mock._channel.exchanges.get("test-exchange")
    assert exchange is not None
    assert len(exchange.publish_calls) == 1
    msg, routing_key = exchange.publish_calls[0]
    assert msg.body == b"test payload"
    assert routing_key == "test.key"


async def test_send_event_uses_hardcoded_defaults(publish_mock):
    await publish_mock.send_event(b"data")

    exchange = publish_mock._channel.exchanges.get("default.in.exchange")
    assert exchange is not None
    _, routing_key = exchange.publish_calls[0]
    assert routing_key == "#"


async def test_send_event_raises_exchange_not_found(publish_mock, monkeypatch):
    import aio_pika

    async def raise_not_found(*args, **kwargs):
        raise aio_pika.exceptions.ChannelNotFoundEntity("no exchange")

    monkeypatch.setattr(publish_mock._channel, "declare_exchange", raise_not_found)

    with pytest.raises(ExchangeNotFound):
        await publish_mock.send_event(b"test", "missing-exchange")


@pytest.mark.parametrize("attribute", ["channel"])
def test_publish_attributes(attribute):
    assert hasattr(Publish, attribute)
