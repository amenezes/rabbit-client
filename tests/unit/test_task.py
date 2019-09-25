import asynctest

from rabbit.task import Task
from rabbit.job import SampleJob


class TestTask(asynctest.TestCase):

    def setUp(self):
        self.task = Task()

    async def test_calling_invalid_job(self):
        custom_task = Task(job=None)
        with self.assertRaises(TypeError):
            await custom_task.process_executor()

    @asynctest.skip
    async def test_process_executor(self):
        result = await self.task.process_executor(
            SampleJob.echo_job,
            1, 2
        )
        self.assertIsInstance(result, list)

    @asynctest.skip
    async def test_std_executor_coroutine(self):
        result = await self.task.std_executor(
            SampleJob.echo_job,
            1, 2
        )
        self.assertIsInstance(result, list)

    @asynctest.skip
    async def test_std_executor_method(self):
        result = await self.task.std_executor(
            SampleJob.echo_job,
            1, 2
        )
        self.assertIsInstance(result, list)
