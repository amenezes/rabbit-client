import asyncio
import types

import asynctest

from rabbit.client import AioRabbitClient
from rabbit.job import echo_job
from rabbit.subscribe import Subscribe
from rabbit.task import Task


class TestSubscribe(asynctest.TestCase):

    async def setUp(self):
        self.subscribe = Subscribe(client=AioRabbitClient())
        self.payload = b'{"a": 1}'

    async def test_execute_process(self):
        subscribe = Subscribe(
            client=AioRabbitClient(),
            task=Task(
                app=asyncio.get_event_loop(),
                job=echo_job
            ),
            task_type='process'
        )
        result = await subscribe._execute(self.payload)
        self.assertIsInstance(result, types.GeneratorType)

    async def test_execute_method(self):
        result = await self.subscribe._execute(self.payload)
        self.assertIsInstance(result, list)
