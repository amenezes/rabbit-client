import pytest

from rabbit.job import async_echo_job

PAYLOAD = b'{"mykey": 123}'


@pytest.mark.asyncio
async def test_async_sample_echo_job():
    response = await async_echo_job(PAYLOAD)
    assert isinstance(response, bytes)
