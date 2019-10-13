import asyncio
import asynctest

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


class TestPublish(asynctest.TestCase):

    async def setUp(self):
        self.publish = Publish(client=AioRabbitClient())

    async def test_set_client_property(self):
        self.publish.client = AioRabbitClient()

    async def test_set_invalid_client_property(self):
        with self.assertRaises(ValueError):
            self.publish.client = None
