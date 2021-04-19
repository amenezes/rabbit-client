import pytest

from rabbit.job import async_echo_job


@pytest.mark.asyncio
async def test_async_echo_job():
    resp = await async_echo_job(b'{"process": 123}')
    assert resp == b'{"process": 123}'
