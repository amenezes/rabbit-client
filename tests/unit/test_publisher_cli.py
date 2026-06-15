import asyncio

import pytest

from rabbit.cli.publisher import Publisher
from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


async def _noop_async(*args, **kwargs):
    pass


@pytest.fixture
def _mock_publisher_deps(monkeypatch):
    monkeypatch.setattr(
        asyncio,
        "get_running_loop",
        lambda: (_ for _ in ()).throw(RuntimeError()),
    )
    monkeypatch.setattr(AioRabbitClient, "connect", _noop_async)
    monkeypatch.setattr(AioRabbitClient, "register", _noop_async)


def test_publisher_stores_exchange_and_routing_key(_mock_publisher_deps):
    publisher = Publisher(exchange_name="ex", routing_key="rk")

    assert publisher.exchange_name == "ex"
    assert publisher.routing_key == "rk"


def test_publisher_configure_publish_returns_publish_instance(_mock_publisher_deps):
    publisher = Publisher(exchange_name="test", routing_key="key")

    assert isinstance(publisher.publish, Publish)


@pytest.mark.parametrize(
    "qtd,expected",
    [(3, 3), (1, 1), (0, 0)],
)
def test_publisher_send_event_calls_send_event_per_qtd(
    _mock_publisher_deps, monkeypatch, qtd, expected
):
    send_event_calls = []

    async def mock_send_event(self, payload, exchange_name, routing_key):
        send_event_calls.append((payload, exchange_name, routing_key))

    monkeypatch.setattr(Publish, "send_event", mock_send_event)

    publisher = Publisher(exchange_name="test", routing_key="key")
    publisher.send_event(b"payload", qtd=qtd, name="test-event")

    assert len(send_event_calls) == expected


def test_publisher_send_event_uses_correct_params(_mock_publisher_deps, monkeypatch):
    send_event_calls = []

    async def mock_send_event(self, payload, exchange_name, routing_key):
        send_event_calls.append((payload, exchange_name, routing_key))

    monkeypatch.setattr(Publish, "send_event", mock_send_event)

    publisher = Publisher(exchange_name="events", routing_key="rk.events")
    publisher.send_event(b"data", qtd=2, name="event")

    assert len(send_event_calls) == 2
    for payload, exchange_name, routing_key in send_event_calls:
        assert payload == b"data"
        assert exchange_name == "events"
        assert routing_key == "rk.events"


def test_publisher_init_forwards_connection_kwargs(_mock_publisher_deps, monkeypatch):
    connect_kwargs = {}

    async def mock_connect(self, **kwargs):
        connect_kwargs.update(kwargs)

    monkeypatch.setattr(AioRabbitClient, "connect", mock_connect)

    Publisher(
        exchange_name="events",
        routing_key="rk",
        host="broker.example.com",
        port=5672,
        login="guest",
    )

    assert connect_kwargs.get("host") == "broker.example.com"
    assert connect_kwargs.get("port") == 5672
    assert connect_kwargs.get("login") == "guest"
