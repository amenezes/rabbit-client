import asyncio

from rabbit.cli.publisher import Publisher
from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


async def test_publisher_stores_exchange_and_routing_key(monkeypatch):
    monkeypatch.setattr(asyncio, "run", lambda coro: None)

    publisher = Publisher(exchange_name="ex", routing_key="rk")
    assert publisher.exchange_name == "ex"
    assert publisher.routing_key == "rk"


async def test_publisher_sends_correct_count(monkeypatch):
    send_calls = []

    async def mock_send_event(self, payload, exchange_name, routing_key):
        send_calls.append((payload, exchange_name, routing_key))

    async def mock_connect(self, **kwargs):
        pass

    async def mock_channel(self):
        return None

    async def mock_close(self):
        pass

    monkeypatch.setattr(Publish, "send_event", mock_send_event)
    monkeypatch.setattr(AioRabbitClient, "connect", mock_connect)
    monkeypatch.setattr(AioRabbitClient, "channel", mock_channel)
    monkeypatch.setattr(AioRabbitClient, "close", mock_close)

    publisher = Publisher(exchange_name="events", routing_key="rk.events")
    await publisher._send_batch(b"data", qtd=3)

    assert len(send_calls) == 3
    for payload, exchange_name, routing_key in send_calls:
        assert payload == b"data"
        assert exchange_name == "events"
        assert routing_key == "rk.events"


async def test_publisher_passes_kwargs_to_client(monkeypatch):
    connect_kwargs = {}

    async def mock_connect(self, **kwargs):
        nonlocal connect_kwargs
        connect_kwargs = kwargs

    async def mock_channel(self):
        return None

    async def mock_close(self):
        pass

    monkeypatch.setattr(AioRabbitClient, "connect", mock_connect)
    monkeypatch.setattr(AioRabbitClient, "channel", mock_channel)
    monkeypatch.setattr(AioRabbitClient, "close", mock_close)

    async def _noop_send(*a, **kw):
        pass

    monkeypatch.setattr(Publish, "send_event", _noop_send)

    publisher = Publisher(
        exchange_name="events",
        routing_key="rk",
        host="broker.example.com",
        port=5672,
        login="guest",
    )
    await publisher._send_batch(b"data", qtd=1)

    assert connect_kwargs.get("host") == "broker.example.com"
    assert connect_kwargs.get("port") == 5672
    assert connect_kwargs.get("login") == "guest"


async def test_publisher_closes_client_after_send(monkeypatch):
    close_called = False

    async def mock_connect(self, **kwargs):
        pass

    async def mock_channel(self):
        return None

    async def mock_close(self):
        nonlocal close_called
        close_called = True

    async def _noop_send(*a, **kw):
        pass

    monkeypatch.setattr(AioRabbitClient, "connect", mock_connect)
    monkeypatch.setattr(AioRabbitClient, "channel", mock_channel)
    monkeypatch.setattr(AioRabbitClient, "close", mock_close)
    monkeypatch.setattr(Publish, "send_event", _noop_send)

    publisher = Publisher(exchange_name="ex", routing_key="rk")
    await publisher._send_batch(b"data", qtd=1)

    assert close_called
