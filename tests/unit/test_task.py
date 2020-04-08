import sys
import types

import pytest

from rabbit import async_echo_job
from rabbit.task import ProcessTask, StandardTask

PAYLOAD = b'{"document": 1, "description": "123", "documentSearchable": null, "pages": [{"body": "abc 123", "number": 1}, {"body": "def 456", "number": 2}, {"body": "ghi 789", "number": 3}]}'


@pytest.mark.asyncio
async def test_process_executor(process_task):
    result = await process_task.execute(PAYLOAD)
    assert isinstance(result, types.GeneratorType)


@pytest.mark.asyncio
async def test_standardtask(standard_task):
    result = await standard_task.execute(PAYLOAD)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_standardtask_with_coro():
    standard_task = StandardTask(async_echo_job)
    result = await standard_task.execute(PAYLOAD)
    assert isinstance(result, list)


@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.version_info > (3, 6), reason="loop dosen't work property in tests on python3.6"
)
async def test_processtask_with_coro(loop):
    process_task = ProcessTask(async_echo_job, loop=loop)
    result = await process_task.execute(PAYLOAD)
    assert isinstance(result, types.GeneratorType)
