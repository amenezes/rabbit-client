import pytest

from rabbit import async_echo_job, echo_job

PAYLOAD = b'{"mykey": 123}'


def test_sample_echo_job():
    response = echo_job(PAYLOAD)
    assert isinstance(response, bytes)


@pytest.mark.asyncio
async def test_async_sample_echo_job():
    response = await async_echo_job(PAYLOAD)
    assert isinstance(response, bytes)
