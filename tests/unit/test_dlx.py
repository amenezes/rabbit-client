import asynctest

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.queue import Queue


class TestDLX(asynctest.TestCase):

    async def setUp(self):
        self.dlx = DLX(
            Queue(name='queue'),
            routing_key='queue'
        )

    async def test_ensure_endswith_dlq(self):
        values = {
            'queue': 'queue.dlq',
            'queue.dlq': 'queue.dlq',
            'a.b.c': 'a.b.c.dlq'
        }
        for value in values.keys():
            with self.subTest(value=value):
                self.assertEqual(
                    await self.dlx._ensure_endswith_dlq(value),
                    values.get(value)
                )

    async def test_get_default_timeout(self):
        result = await self.dlx._get_timeout(None)
        self.assertEqual(result, 5000)

    async def test_get_cycle_timeout(self):
        values = {1: 5000, 2: 25000, 3: 125000}
        for i in values.keys():
            result = await self.dlx._get_timeout(
                {'x-delay': values.get(i)}
            )
            self.assertEqual(result, int(values.get(i) * 5))

    async def test_client_property(self):
        self.assertIsNone(self.dlx.client)

    async def test_set_invalid_client_property(self):
        with self.assertRaises(ValueError):
            self.dlx.client = None

    async def test_set_client_property(self):
        self.dlx.client = AioRabbitClient()
