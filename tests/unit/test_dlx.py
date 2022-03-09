import pytest

from rabbit.exceptions import OperationError
from tests.conftest import EnvelopeMock, PropertiesMock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value,expected",
    [("queue", "queue.dlq"), ("queue.dlq", "queue.dlq"), ("a.b.c", "a.b.c.dlq")],
)
async def test_ensure_endswith_dlq(dlx, value, expected):
    result = await dlx._ensure_endswith_dlq(value)
    assert result == expected


@pytest.mark.asyncio
async def test_send_event_error_without_client_connection(dlx):
    with pytest.raises(OperationError):
        await dlx.send_event(Exception, bytes(), EnvelopeMock(), PropertiesMock())


@pytest.mark.asyncio
async def test_configure(dlx_mock):
    await dlx_mock.configure()


def test_dlx_repr(dlx):
    assert isinstance(repr(dlx), str)
