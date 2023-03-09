from rabbit.job import async_echo_job


async def test_async_echo_job():
    resp = await async_echo_job(b'{"process": 123}', skip_wait=True)
    assert resp == b'{"process": 123}'
