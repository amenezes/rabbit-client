import asyncio

import asynctest

from rabbit.job import SampleJob
from rabbit.subscribe import Subscribe
from rabbit.task import Task


class TestSubscribe(asynctest.TestCase):

    async def setUp(self):
        self.subscribe = Subscribe()
        self.payload = b'{"a": 1}'

    async def test_execute_process(self):
        subscribe = Subscribe(
            task=Task(
                app=asyncio.get_event_loop(),
                job=SampleJob.echo_job
            ),
            task_type='process'
        )
        result = await subscribe._execute(self.payload)
        self.assertIsInstance(result, list)

    async def test_execute_method(self):
        result = await self.subscribe._execute(self.payload)
        self.assertIsInstance(result, list)
