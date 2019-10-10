import asynctest

from rabbit.client import AioRabbitClient
from rabbit.dlx import DLX
from rabbit.exceptions import OperationError
from rabbit.queue import Queue

from tests.integration.setup import EnvelopeMock, PropertiesMock


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
        self.assertEqual(result, 25000)

    async def test_get_cycle_timeout(self):
        values = {1: 5000, 2: 25000, 3: 125000}
        for i in values.keys():
            result = await self.dlx._get_timeout(
                {'x-delay': values.get(i)}
            )
            self.assertEqual(result, int(values.get(i) * 5))

    async def test_client_property(self):
        self.assertIsNone(self.dlx.client)

    @asynctest.skip
    async def test_set_invalid_client_property(self):
        with self.assertRaises(ValueError):
            self.dlx.client = None

    async def test_set_client_property(self):
        self.dlx.client = AioRabbitClient()

    async def test_send_event_error_without_client_connection(self):
        dlx = DLX(Queue('test'), '#')
        with self.assertRaises(OperationError):
            await dlx.send_event(
                Exception, bytes(), EnvelopeMock(), PropertiesMock()
            )
