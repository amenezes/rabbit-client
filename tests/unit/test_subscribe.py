import pytest

from rabbit.dlx import DLX
from rabbit.exceptions import ClientNotConnectedError
from rabbit.job import async_echo_job
from rabbit.subscribe import Subscribe


async def test_configure_raises_when_not_connected(subscribe):
    with pytest.raises(ClientNotConnectedError):
        await subscribe.configure()


async def test_configure_declares_exchange_and_queue(subscribe_mock, mock_channel):
    await subscribe_mock.configure(mock_channel)

    assert "default.in.exchange" in mock_channel.exchanges
    assert "default.subscribe.queue" in mock_channel.queues


async def test_configure_sets_prefetch_to_concurrent(mock_channel):
    subscribe = Subscribe(task=async_echo_job, concurrent=4)
    await subscribe.configure(mock_channel)

    assert mock_channel.qos_prefetch == 4


async def test_configure_starts_consuming(subscribe_mock, mock_channel):
    await subscribe_mock.configure(mock_channel)

    queue = mock_channel.queues["default.subscribe.queue"]
    assert queue.consume_callback is not None
    assert queue.consume_callback == subscribe_mock._handle_message


async def test_configure_binds_queue_to_exchange(subscribe_mock, mock_channel):
    await subscribe_mock.configure(mock_channel)

    queue = mock_channel.queues["default.subscribe.queue"]
    assert len(queue.bind_calls) >= 1


async def test_configure_declares_dlx_topology(subscribe_mock, mock_channel):
    await subscribe_mock.configure(mock_channel)

    assert "DLX" in mock_channel.exchanges
    assert "dlqReRouter.default.in.exchange" in mock_channel.exchanges
    assert "default.subscribe.queue.dlq" in mock_channel.queues


async def test_handle_message_acks_on_success(
    subscribe_mock, mock_channel, mock_message
):
    await subscribe_mock.configure(mock_channel)

    await subscribe_mock._handle_message(mock_message)

    assert mock_message.acked


async def test_handle_message_acks_after_dlx_on_error(
    subscribe_mock, mock_channel, mock_message, monkeypatch
):
    send_called = False

    async def track_send(self, cause, message):
        nonlocal send_called
        send_called = True

    monkeypatch.setattr(DLX, "send_event", track_send)

    async def failing_task(message):
        raise ValueError("processing error")

    subscribe_mock.task = failing_task
    await subscribe_mock.configure(mock_channel)

    await subscribe_mock._handle_message(mock_message)

    assert send_called
    assert mock_message.acked


async def test_handle_message_acks_even_when_dlx_fails(
    subscribe_mock, mock_channel, mock_message, monkeypatch
):
    async def failing_send(self, cause, message):
        raise RuntimeError("DLX unavailable")

    monkeypatch.setattr(DLX, "send_event", failing_send)

    async def failing_task(message):
        raise ValueError("processing error")

    subscribe_mock.task = failing_task
    await subscribe_mock.configure(mock_channel)

    await subscribe_mock._handle_message(mock_message)

    assert mock_message.acked


async def test_handle_message_does_not_ack_before_task_completes(
    subscribe_mock, mock_channel, mock_message
):
    await subscribe_mock.configure(mock_channel)

    task_ran = False

    async def tracking_task(message):
        nonlocal task_ran
        task_ran = True

    subscribe_mock.task = tracking_task

    await subscribe_mock._handle_message(mock_message)

    assert task_ran
    assert mock_message.acked


@pytest.mark.parametrize(
    "attribute", ["task", "exchange", "queue", "concurrent", "delay_strategy"]
)
def test_subscribe_attributes(attribute):
    assert hasattr(Subscribe, attribute)


async def test_subscribe_creates_dlx_in_post_init():
    subscribe = Subscribe(task=async_echo_job)
    assert isinstance(subscribe._dlx, DLX)


async def test_subscribe_dlx_has_correct_exchange_names():
    subscribe = Subscribe(task=async_echo_job)
    assert subscribe._dlx.exchange.name == "DLX"
    assert subscribe._dlx.dlq_exchange.name == "dlqReRouter.default.in.exchange"
