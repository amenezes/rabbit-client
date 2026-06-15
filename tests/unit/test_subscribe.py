import asyncio

import pytest

from rabbit.dlx import DLX
from rabbit.exceptions import ClientNotConnectedError
from rabbit.subscribe import Subscribe
from tests.conftest import PropertiesMock


async def test_register_subscribe_without_client_connected(subscribe):
    with pytest.raises(ClientNotConnectedError):
        await subscribe.configure()


async def test_run_sends_error_to_dlx(subscribe_mock, monkeypatch, envelope_mock):
    send_event_calls = []

    async def track_send_event(self, cause, body, envelope, properties):
        send_event_calls.append(True)

    async def failing_task(body, envelope, properties):
        raise ValueError("processing error")

    monkeypatch.setattr(DLX, "send_event", track_send_event)
    subscribe_mock.task = failing_task
    subscribe_mock._job_queue.put_nowait((b"body", envelope_mock, PropertiesMock()))

    await subscribe_mock._run()

    assert len(send_event_calls) == 1
    assert subscribe_mock._job_queue.qsize() == 0


async def test_subscribe_run_acks_on_success(
    subscribe_mock, monkeypatch, envelope_mock
):
    ack_called = False

    async def track_ack(self, envelope, multiple=False):
        nonlocal ack_called
        ack_called = True

    async def success_task(body, envelope, properties):
        pass

    monkeypatch.setattr(subscribe_mock.__class__, "ack_event", track_ack)
    subscribe_mock.task = success_task
    subscribe_mock._job_queue.put_nowait((b"body", envelope_mock, PropertiesMock()))

    await subscribe_mock._run()

    assert ack_called
    assert subscribe_mock._job_queue.qsize() == 0


async def test_subscribe_callback_enqueues_message(subscribe_mock, envelope_mock):
    body = b"test message"
    envelope = envelope_mock
    properties = PropertiesMock()

    await subscribe_mock.callback(None, body, envelope, properties)

    assert subscribe_mock._job_queue.qsize() == 1
    queued = subscribe_mock._job_queue.get_nowait()
    assert queued[0] == body
    assert queued[1] is envelope
    assert queued[2] is properties


async def test_subscribe_callback_nacks_when_queue_full(
    subscribe_mock, monkeypatch, envelope_mock
):
    nack_called = False

    async def track_nack(self, envelope, multiple=False, requeue=True):
        nonlocal nack_called
        nack_called = True

    monkeypatch.setattr(subscribe_mock.__class__, "nack_event", track_nack)

    subscribe_mock._job_queue.put_nowait((b"first", envelope_mock, PropertiesMock()))

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            subscribe_mock.callback(None, b"second", envelope_mock, PropertiesMock()),
            timeout=0.1,
        )

    assert nack_called


@pytest.mark.parametrize(
    "attribute", ["task", "exchange", "queue", "concurrent", "delay_strategy"]
)
def test_subscribe_attributes(attribute):
    assert hasattr(Subscribe, attribute)


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
