import pytest

from rabbit.dlx import DLX
from rabbit.exceptions import OperationError
from tests.conftest import PropertiesMock


@pytest.mark.parametrize(
    "value,expected",
    [("queue", "queue.dlq"), ("queue.dlq", "queue.dlq"), ("a.b.c", "a.b.c.dlq")],
)
async def test_ensure_endswith_dlq(dlx, value, expected):
    result = await dlx._ensure_endswith_dlq(value)
    assert result == expected


async def test_send_event_error_without_client_connection(dlx, envelope_mock):
    with pytest.raises(OperationError):
        await dlx.send_event(Exception, bytes(), envelope_mock, PropertiesMock())


async def test_dlx_get_properties_creates_default_headers(dlx, envelope_mock):
    properties = PropertiesMock(headers=None)
    result = await dlx._get_properties(
        5000, ValueError("err"), envelope_mock, properties
    )

    assert result["expiration"] == "5000"
    assert result["headers"]["x-delay"] == "5000"
    assert result["headers"]["x-exception-message"] == "err"
    assert result["headers"]["x-original-exchange"] == "src-exchange"
    assert result["headers"]["x-original-routingKey"] == "#"


async def test_dlx_get_properties_merges_original_headers(dlx, envelope_mock):
    properties = PropertiesMock(
        headers={"custom-key": "custom-value", "x-delay": "9999"}
    )
    result = await dlx._get_properties(
        5000, ValueError("err"), envelope_mock, properties
    )

    assert result["headers"]["custom-key"] == "custom-value"
    assert result["headers"]["x-delay"] == "9999"


@pytest.mark.parametrize(
    "attribute", ["exchange", "dlq_exchange", "queue", "delay_strategy", "channel"]
)
def test_dlx_attributes(attribute):
    assert hasattr(DLX, attribute)


async def test_dlx_configure_runs_channel_commands_sequentially(
    dlx, recording_channel, skip_configure_delays
):
    # Regression: bug-rabbit-client_8.md — DLX.configure() também exigia sequencial.
    dlx.channel = recording_channel

    await dlx.configure()

    method_order = [name for name, _ in recording_channel.calls]
    assert method_order == [
        "queue_declare",
        "exchange_declare",
        "exchange_declare",
        "queue_bind",
        "queue_bind",
    ]
    assert recording_channel.overlaps == 0
