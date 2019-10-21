import asyncio

import asynctest

from rabbit.job import async_echo_job, echo_job
from rabbit.task import Task


class TestTask(asynctest.TestCase):

    async def setUp(self):
        self.task = Task()
        self.payload = b'{"document": 1, "description": "123", "documentSearchable": null, "pages": [{"body": "abc 123", "number": 1}, {"body": "def 456", "number": 2}, {"body": "ghi 789", "number": 3}]}'

    async def test_calling_invalid_job(self):
        custom_task = Task(job=None)
        with self.assertRaises(TypeError):
            await custom_task.process_executor()

    async def test_process_executor(self):
        task = Task(
            app=asyncio.get_event_loop(),
            job=echo_job
        )
        result = await task.process_executor(self.payload)
        self.assertIsInstance(result, list)

    async def test_std_executor_coroutine(self):
        task = Task(job=async_echo_job)
        result = await task.std_executor(self.payload)
        self.assertIsInstance(result, list)

    async def test_std_executor_blocking_method(self):
        task = Task(job=echo_job)
        result = await task.std_executor(self.payload)
        self.assertIsInstance(result, list)

    async def test_invalid_std_executor(self):
        task = Task(job=None)
        with self.assertRaises(TypeError):
            await task.std_executor(self.payload)
