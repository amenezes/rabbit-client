import pytest

from rabbit.dlx import DLX
from tests.conftest import MockMessage


async def test_dlx_configure_declares_dlx_exchange(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    assert "dlx" in mock_channel.exchanges


async def test_dlx_configure_declares_dlq_router_exchange(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    assert "dlq_rerouter" in mock_channel.exchanges


async def test_dlx_configure_declares_retry_queue(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    assert "queue.dlq" in mock_channel.queues


async def test_dlx_configure_binds_retry_queue_to_dlx_exchange(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    retry_queue = mock_channel.queues["queue.dlq"]
    assert len(retry_queue.bind_calls) == 1
    bound_exchange, routing_key = retry_queue.bind_calls[0]
    assert bound_exchange.name == "dlx"
    assert routing_key == "queue"


async def test_dlx_configure_binds_main_queue_to_dlq_router(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    assert len(main_queue.bind_calls) == 1
    bound_exchange, routing_key = main_queue.bind_calls[0]
    assert bound_exchange.name == "dlq_rerouter"
    assert routing_key == "queue"


async def test_send_event_publishes_with_expiration(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    message = MockMessage(
        body=b"error-body",
        headers={"x-delay": 5000},
        exchange="src-exchange",
        routing_key="test.key",
    )

    await dlx.send_event(ValueError("boom"), message)

    dlx_exchange = mock_channel.exchanges["dlx"]
    assert len(dlx_exchange.publish_calls) == 1
    published_msg, routing_key = dlx_exchange.publish_calls[0]
    assert routing_key == "queue"
    assert published_msg.body == b"error-body"


async def test_send_event_sets_headers(dlx, mock_channel):
    main_queue = await mock_channel.declare_queue("queue")
    await dlx.configure(mock_channel, main_queue)

    message = MockMessage(
        body=b"error-body",
        headers={"x-delay": 5000},
        exchange="src-exchange",
        routing_key="test.key",
    )

    await dlx.send_event(ValueError("boom"), message)

    dlx_exchange = mock_channel.exchanges["dlx"]
    published_msg, _ = dlx_exchange.publish_calls[0]
    assert "x-delay" in published_msg.headers
    assert "x-exception-message" in published_msg.headers
    assert "x-original-exchange" in published_msg.headers
    assert published_msg.headers["x-original-exchange"] == "src-exchange"


async def test_send_event_raises_when_not_configured(dlx):
    message = MockMessage(body=b"body")

    with pytest.raises(RuntimeError, match="DLX not configured"):
        await dlx.send_event(ValueError("err"), message)


@pytest.mark.parametrize(
    "value,expected",
    [("queue", "queue.dlq"), ("queue.dlq", "queue.dlq"), ("a.b.c", "a.b.c.dlq")],
)
async def test_ensure_endswith_dlq(dlx, value, expected):
    result = await dlx._ensure_endswith_dlq(value)
    assert result == expected


@pytest.mark.parametrize(
    "attribute", ["exchange", "dlq_exchange", "queue", "delay_strategy"]
)
def test_dlx_attributes(attribute):
    assert hasattr(DLX, attribute)
