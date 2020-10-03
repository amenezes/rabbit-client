import pytest

from conftest import AioRabbitClientMock, EnvelopeMock, PropertiesMock
from rabbit.dlx import DLX
from rabbit.exceptions import AttributeNotInitialized


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value,expected",
    [("queue", "queue.dlq"), ("queue.dlq", "queue.dlq"), ("a.b.c", "a.b.c.dlq")],
)
async def test_ensure_endswith_dlq(dlx, value, expected):
    result = await dlx._ensure_endswith_dlq(value)
    assert result == expected


@pytest.mark.asyncio
async def test_get_default_timeout(dlx):
    result = await dlx._get_timeout(None)
    assert result == 25000


@pytest.mark.asyncio
async def test_get_cycle_timeout(dlx):
    values = {1: 5000, 2: 25000, 3: 125000}
    for i in values.keys():
        result = await dlx._get_timeout({"x-delay": values.get(i)})
        assert result == int(values.get(i) * 5)


@pytest.mark.asyncio
async def test_send_event_error_without_client_connection(dlx):
    with pytest.raises(AttributeNotInitialized):
        await dlx.send_event(Exception, bytes(), EnvelopeMock(), PropertiesMock())


@pytest.mark.asyncio
async def test_configure():
    dlx = DLX(AioRabbitClientMock())
    await dlx.configure()


@pytest.mark.asyncio
async def test_configure_exchange():
    dlx = DLX(AioRabbitClientMock())
    await dlx._configure_exchange()


@pytest.mark.asyncio
async def test_configure_queue():
    dlx = DLX(AioRabbitClientMock())
    await dlx._configure_queue()


@pytest.mark.asyncio
async def test_configure_queue_bind():
    dlx = DLX(AioRabbitClientMock())
    await dlx._configure_queue_bind()
