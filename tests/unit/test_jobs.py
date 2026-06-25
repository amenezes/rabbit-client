import pytest

from rabbit.job import async_chaos_job, async_echo_job
from tests.conftest import MockMessage


async def test_async_echo_job():
    message = MockMessage(body=b'{"process": 123}')
    await async_echo_job(message)


@pytest.mark.xfail(reason="The test may fail due to randomness issue")
async def test_async_chaos_job():
    message = MockMessage(body=b'{"process": 123}')
    await async_chaos_job(message)
