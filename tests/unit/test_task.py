import asynctest

from rabbit.job import SampleJob
from rabbit.task import Task


class TestTask(asynctest.TestCase):

    def setUp(self):
        self.task = Task()
        self.job = SampleJob()

    async def test_calling_invalid_job(self):
        custom_task = Task(job=None)
        with self.assertRaises(TypeError):
            await custom_task.process_executor()

    @asynctest.skip
    async def test_process_executor(self):
        # task = Task(job=self.job.async_echo_job)
        result = await self.task.process_executor(1, 2)
        self.assertIsInstance(result, list)

    async def test_std_executor_coroutine(self):
        task = Task(job=self.job.async_echo_job)
        result = await task.std_executor(1, 2)
        self.assertIsInstance(result, list)

    async def test_std_executor_blocking_method(self):
        task = Task(job=self.job.echo_job)
        result = await task.std_executor(1, 2)
        self.assertIsInstance(result, list)

    async def test_invalid_std_executor(self):
        task = Task(job=None)
        with self.assertRaises(TypeError):
            await task.std_executor(1, 2)
