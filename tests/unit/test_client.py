import aio_pika
import pytest

from rabbit.client import AioRabbitClient


async def test_connect_and_channel(client, monkeypatch):
    connect_calls = 0

    async def mock_connect_robust(*args, **kwargs):
        nonlocal connect_calls
        connect_calls += 1
        return aio_pika.RobustConnection

    monkeypatch.setattr(aio_pika, "connect_robust", mock_connect_robust)

    await client.connect(url="amqp://guest:guest@localhost:5672/%2F")
    assert connect_calls == 1


async def test_channel_raises_when_not_connected(client):
    with pytest.raises(RuntimeError):
        await client.channel()


async def test_connect_builds_url_from_kwargs(client, monkeypatch):
    received_kwargs = {}

    async def mock_connect_robust(**kwargs):
        nonlocal received_kwargs
        received_kwargs = kwargs
        return aio_pika.RobustConnection

    monkeypatch.setattr(aio_pika, "connect_robust", mock_connect_robust)

    await client.connect(
        host="myhost", port=5673, login="user", password="pass", virtualhost="vh"
    )
    assert received_kwargs["host"] == "myhost"
    assert received_kwargs["port"] == 5673
    assert received_kwargs["login"] == "user"
    assert received_kwargs["password"] == "pass"
    assert received_kwargs["virtualhost"] == "vh"


async def test_close_when_not_connected(client):
    await client.close()


async def test_is_connected_returns_false_when_not_connected(client):
    assert not client.is_connected


async def test_async_context_manager(client, monkeypatch):
    enter_called = False
    exit_called = False

    async def mock_connect_robust(**kwargs):
        return aio_pika.RobustConnection

    async def mock_close():
        nonlocal exit_called
        exit_called = True

    monkeypatch.setattr(aio_pika, "connect_robust", mock_connect_robust)
    monkeypatch.setattr(aio_pika.RobustConnection, "close", mock_close)

    async with client:
        enter_called = True
        await client.connect()

    assert enter_called
    assert exit_called


@pytest.mark.skip(reason="Legacy: server_properties removed in Phase 1")
def test_server_properties_with_client_not_connected(client):
    assert client.server_properties is None


@pytest.mark.skip(reason="Legacy: server_properties removed in Phase 1")
def test_server_properties(client_mock):
    assert isinstance(client_mock.server_properties, dict)


@pytest.mark.skip(reason="Legacy: persistent_connect removed in Phase 1")
async def test_persistent_connect_backoff(client, monkeypatch):
    pass


@pytest.mark.skip(reason="Legacy: watch_connection_state removed in Phase 1")
async def test_watch_connection_state_clears_event_after_recovery(
    client_mock, subscribe_mock, monkeypatch
):
    pass


@pytest.mark.skip(reason="Legacy: watch_connection_state removed in Phase 1")
async def test_watch_connection_state_clears_event_on_failure(
    client_mock, subscribe_mock, monkeypatch
):
    pass


@pytest.mark.skip(reason="Legacy: watch_channel_state removed in Phase 1")
async def test_watch_channel_state_recovers_closed_channel(
    client_mock, subscribe_mock, monkeypatch
):
    pass


@pytest.mark.skip(reason="Legacy: persistent_connect removed in Phase 1")
async def test_persistent_connect_closes_transport_on_cancellation(client, monkeypatch):
    pass


def test_client_repr(client):
    assert "AioRabbitClient" in repr(client)


@pytest.mark.parametrize("attribute", ["connect", "channel", "close", "is_connected"])
def test_client_attributes(attribute):
    assert hasattr(AioRabbitClient, attribute)
