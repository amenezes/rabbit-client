import pytest

from rabbit.exceptions import OperationError
from tests.conftest import EnvelopeMock, PropertiesMock


@pytest.mark.parametrize(
    "value,expected",
    [("queue", "queue.dlq"), ("queue.dlq", "queue.dlq"), ("a.b.c", "a.b.c.dlq")],
)
async def test_ensure_endswith_dlq(dlx, value, expected):
    result = await dlx._ensure_endswith_dlq(value)
    assert result == expected


async def test_send_event_error_without_client_connection(dlx):
    with pytest.raises(OperationError):
        await dlx.send_event(Exception, bytes(), EnvelopeMock(), PropertiesMock())


def test_dlx_repr(dlx):
    assert isinstance(repr(dlx), str)
