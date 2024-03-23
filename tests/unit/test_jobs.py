import pytest

from rabbit.job import async_chaos_job, async_echo_job


async def test_async_echo_job():
    resp = await async_echo_job(b'{"process": 123}', skip_wait=True)
    assert resp == b'{"process": 123}'


@pytest.mark.xfail(reason="The test may fail due to randomness issue")
async def test_async_chaos_job():
    resp = await async_chaos_job(b'{"process": 123}', skip_wait=True)
    assert resp == b'{"process": 123}'
