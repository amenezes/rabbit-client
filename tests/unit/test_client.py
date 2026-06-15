import asyncio

import pytest

from rabbit.client import AioRabbitClient, aioamqp
from rabbit.exceptions import AttributeNotInitialized
from rabbit.subscribe import Subscribe
from tests.conftest import AioAmqpMock


async def aioamqp_mock(*args, **kwargs):
    aioamqp_mock = AioAmqpMock()
    transport, protocol = await aioamqp_mock.connect(args, kwargs)
    return transport, protocol


async def test_connect(client, monkeypatch):
    monkeypatch.setattr(aioamqp, "connect", aioamqp_mock)
    await client.connect()
    channel = await client.get_channel()
    assert channel is not None


async def test_channel_not_initialized(client):
    with pytest.raises(AttributeNotInitialized):
        await client.get_channel()


async def test_watch_connection_state_clears_event_after_recovery(
    client_mock, subscribe_mock, monkeypatch
):
    async def _fast_configure(self, channel=None):
        pass

    monkeypatch.setattr(Subscribe, "configure", _fast_configure)

    client_mock._event.set()
    task = asyncio.create_task(client_mock.watch_connection_state(subscribe_mock))
    await asyncio.sleep(0.1)
    assert not client_mock._event.is_set()
    task.cancel()


async def test_watch_connection_state_clears_event_on_failure(
    client_mock, subscribe_mock, monkeypatch
):
    async def raising_get_channel():
        raise AttributeNotInitialized()

    monkeypatch.setattr(client_mock, "get_channel", raising_get_channel)
    client_mock._event.set()

    task = asyncio.create_task(client_mock.watch_connection_state(subscribe_mock))
    await asyncio.sleep(0.5)

    assert not client_mock._event.is_set()
    task.cancel()


def test_client_repr(client):
    assert (
        repr(client)
        == "AioRabbitClient(connected=False, channels=0, max_channels=0, background_tasks=BackgroundTasks(tasks=0, tasks_by_name=[]))"
    )


def test_server_properties_with_client_not_connected(client):
    assert client.server_properties is None


def test_server_properties(client_mock):
    assert isinstance(client_mock.server_properties, dict)


async def test_persistent_connect_backoff(client, monkeypatch):
    connect_attempts = 0
    sleep_delays = []

    async def mock_connect(**kwargs):
        nonlocal connect_attempts
        connect_attempts += 1
        raise OSError("connection refused")

    _original_sleep = asyncio.sleep

    async def mock_sleep(delay):
        sleep_delays.append(delay)
        await _original_sleep(0)

    monkeypatch.setattr(aioamqp, "connect", mock_connect)
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    task = asyncio.create_task(client.persistent_connect())

    for _ in range(50):
        if connect_attempts >= 5:
            break
        await _original_sleep(0.01)

    task.cancel()
    await _original_sleep(0)

    assert connect_attempts >= 5
    assert sleep_delays[0] == 1
    assert sleep_delays[1] == 2
    assert sleep_delays[2] == 4


async def test_watch_channel_state_recovers_closed_channel(
    client_mock, subscribe_mock, monkeypatch
):
    configure_called = False
    _original_sleep = asyncio.sleep

    async def track_configure(self, channel=None):
        nonlocal configure_called
        configure_called = True

    async def noop_sleep(delay):
        await _original_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", noop_sleep)
    monkeypatch.setattr(subscribe_mock.__class__, "configure", track_configure)

    subscribe_mock._channel.is_open = False

    task = asyncio.create_task(client_mock.watch_channel_state(subscribe_mock))
    await _original_sleep(0.05)
    task.cancel()
    await _original_sleep(0)

    assert configure_called


@pytest.mark.parametrize("attribute", ["transport", "server_properties", "protocol"])
def test_client_attributes(attribute):
    assert hasattr(AioRabbitClient, attribute)


async def test_persistent_connect_closes_transport_on_cancellation(client, monkeypatch):
    close_calls = []

    class MockTransport:
        def close(self):
            close_calls.append(True)

    transport = MockTransport()

    async def mock_wait_closed(self):
        await asyncio.Event().wait()

    protocol = type("MockProtocol", (), {"wait_closed": mock_wait_closed})()

    async def mock_connect(**kwargs):
        return transport, protocol

    monkeypatch.setattr(aioamqp, "connect", mock_connect)

    task = asyncio.create_task(client.persistent_connect())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(close_calls) >= 1
