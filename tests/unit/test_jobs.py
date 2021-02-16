import pytest

from rabbit.job import async_echo_job, dlx_job


@pytest.mark.asyncio
async def test_async_echo_job():
    resp = await async_echo_job(b'{"process": 123}')
    assert resp == b'{"process": 123}'


@pytest.mark.asyncio
async def test_dlx_job():
    with pytest.raises(Exception):
        await dlx_job(b'{"process": 123}')
