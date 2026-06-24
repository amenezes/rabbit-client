import asyncio

import pytest

from rabbit.dlx import DLX
from rabbit.exceptions import ClientNotConnectedError
from rabbit.job import async_echo_job
from rabbit.subscribe import Subscribe
from tests.conftest import PropertiesMock


async def _run_with_task(subscribe_mock, envelope_mock, task):
    subscribe_mock.task = task
    subscribe_mock._job_queue.put_nowait((b"body", envelope_mock, PropertiesMock()))
    await subscribe_mock._run()


async def test_register_subscribe_without_client_connected(subscribe):
    with pytest.raises(ClientNotConnectedError):
        await subscribe.configure()


async def test_run_dispatches_to_dlx_when_task_raises(
    subscribe_mock, monkeypatch, envelope_mock
):
    send_event_calls = []

    async def track_send_event(self, cause, body, envelope, properties):
        send_event_calls.append(True)

    async def failing_task(body, envelope, properties):
        raise ValueError("processing error")

    monkeypatch.setattr(DLX, "send_event", track_send_event)
    await _run_with_task(subscribe_mock, envelope_mock, failing_task)

    assert len(send_event_calls) == 1


async def test_run_drains_queue_after_error(subscribe_mock, monkeypatch, envelope_mock):
    async def failing_task(body, envelope, properties):
        raise ValueError("processing error")

    await _run_with_task(subscribe_mock, envelope_mock, failing_task)

    assert subscribe_mock._job_queue.qsize() == 0


async def test_run_acks_message_when_task_succeeds(
    subscribe_mock, monkeypatch, envelope_mock
):
    ack_called = False

    async def track_ack(self, envelope, multiple=False):
        nonlocal ack_called
        ack_called = True

    async def success_task(body, envelope, properties):
        pass

    monkeypatch.setattr(subscribe_mock.__class__, "ack_event", track_ack)
    await _run_with_task(subscribe_mock, envelope_mock, success_task)

    assert ack_called


async def test_run_drains_queue_when_task_succeeds(
    subscribe_mock, monkeypatch, envelope_mock
):
    async def success_task(body, envelope, properties):
        pass

    await _run_with_task(subscribe_mock, envelope_mock, success_task)

    assert subscribe_mock._job_queue.qsize() == 0


async def test_subscribe_callback_enqueues_one_item(subscribe_mock, envelope_mock):
    await subscribe_mock.callback(
        None, b"test message", envelope_mock, PropertiesMock()
    )

    assert subscribe_mock._job_queue.qsize() == 1


async def test_subscribe_callback_preserves_enqueued_content(
    subscribe_mock, envelope_mock
):
    body = b"test message"
    envelope = envelope_mock
    properties = PropertiesMock()

    await subscribe_mock.callback(None, body, envelope, properties)

    queued = subscribe_mock._job_queue.get_nowait()
    assert queued[0] == body
    assert queued[1] is envelope
    assert queued[2] is properties



@pytest.mark.parametrize(
    "attribute", ["task", "exchange", "queue", "concurrent", "delay_strategy"]
)
def test_subscribe_attributes(attribute):
    assert hasattr(Subscribe, attribute)


async def _setup_cancellation_test(
    subscribe_mock, monkeypatch, envelope_mock, track_ack, track_send
):
    monkeypatch.setattr(subscribe_mock.__class__, "ack_event", track_ack)
    monkeypatch.setattr(DLX, "send_event", track_send)

    async def failing_task(body, envelope, properties):
        raise ValueError("processing error")

    subscribe_mock.task = failing_task
    subscribe_mock._job_queue.put_nowait((b"body", envelope_mock, PropertiesMock()))


async def test_run_survives_cancellation_during_dlx_send(
    subscribe_mock, monkeypatch, envelope_mock
):
    ack_called = False
    send_called = False

    async def track_ack(self, envelope, multiple=False):
        nonlocal ack_called
        ack_called = True

    async def track_send(self, cause, body, envelope, properties):
        nonlocal send_called
        send_called = True

    await _setup_cancellation_test(
        subscribe_mock, monkeypatch, envelope_mock, track_ack, track_send
    )

    original_wait_for = asyncio.wait_for
    call_count = 0

    async def mock_wait_for(fut, timeout=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise asyncio.CancelledError()
        return await original_wait_for(fut, timeout=timeout)

    monkeypatch.setattr(asyncio, "wait_for", mock_wait_for)

    with pytest.raises(asyncio.CancelledError):
        await subscribe_mock._run()

    assert ack_called
    assert send_called
    assert call_count == 2


async def test_run_survives_double_cancellation_during_dlx_send(
    subscribe_mock, monkeypatch, envelope_mock
):
    ack_called = False
    send_called = False

    async def track_ack(self, envelope, multiple=False):
        nonlocal ack_called
        ack_called = True

    async def track_send(self, cause, body, envelope, properties):
        nonlocal send_called
        send_called = True

    await _setup_cancellation_test(
        subscribe_mock, monkeypatch, envelope_mock, track_ack, track_send
    )

    call_count = 0

    async def mock_wait_for(fut, timeout=None):
        nonlocal call_count
        call_count += 1
        raise asyncio.CancelledError()

    monkeypatch.setattr(asyncio, "wait_for", mock_wait_for)

    with pytest.raises(asyncio.CancelledError):
        await subscribe_mock._run()

    assert not ack_called
    assert not send_called
    assert call_count == 2


async def test_subscribe_run_does_not_call_task_done_when_queue_get_fails(
    subscribe_mock, monkeypatch
):
    task_done_calls = []

    async def mock_get():
        raise RuntimeError("queue error")

    def mock_task_done():
        task_done_calls.append(True)

    monkeypatch.setattr(subscribe_mock._job_queue, "get", mock_get)
    monkeypatch.setattr(subscribe_mock._job_queue, "task_done", mock_task_done)

    await subscribe_mock._run()

    assert len(task_done_calls) == 0


async def test_configure_runs_channel_commands_sequentially(
    subscribe, recording_channel, skip_configure_delays
):
    # Regression: bug-rabbit-client_8.md — canais AMQP exigem RPC sequencial.
    subscribe.channel = recording_channel

    await subscribe.configure()

    method_order = [name for name, _ in recording_channel.calls]
    assert method_order == [
        "basic_qos",
        "queue_declare",
        "queue_declare",
        "exchange_declare",
        "exchange_declare",
        "queue_bind",
        "queue_bind",
        "exchange_declare",
        "queue_bind",
        "basic_consume",
    ]
    assert recording_channel.overlaps == 0


@pytest.mark.parametrize("concurrent", [1, 4, 16])
async def test_configure_sets_basic_qos_prefetch_to_concurrent(
    concurrent, recording_channel, skip_configure_delays
):
    subscribe = Subscribe(task=async_echo_job, concurrent=concurrent)
    subscribe.channel = recording_channel

    await subscribe.configure()

    assert recording_channel.calls[0] == ("basic_qos", concurrent)


async def test_run_serialized_by_semaphore_when_concurrent_1(
    subscribe_mock, envelope_mock
):
    subscribe_mock._semaphore = asyncio.Semaphore(1)

    running = 0
    max_concurrent = 0
    started = asyncio.Event()

    async def slow_task(body, envelope, properties):
        nonlocal running, max_concurrent
        running += 1
        max_concurrent = max(max_concurrent, running)
        started.set()
        await asyncio.sleep(0.1)
        running -= 1

    subscribe_mock.task = slow_task
    subscribe_mock._job_queue.put_nowait((b"msg1", envelope_mock, PropertiesMock()))

    t1 = asyncio.create_task(subscribe_mock._run())
    await started.wait()

    subscribe_mock._job_queue.put_nowait((b"msg2", envelope_mock, PropertiesMock()))
    t2 = asyncio.create_task(subscribe_mock._run())

    await asyncio.sleep(0.05)
    assert running == 1
    assert max_concurrent == 1

    await asyncio.gather(t1, t2)
    assert max_concurrent == 1
    assert running == 0
