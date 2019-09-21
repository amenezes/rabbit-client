import asyncio

import asynctest

from rabbit.client import AioRabbitClient


class TestClient(asynctest.TestCase):

    async def setUp(self):
        loop = asyncio.get_event_loop()
        self.client = AioRabbitClient(app=loop)
        self.payload = {"message": "aiorabbitclient test."}

    async def test_client_default_execution(self):
        await self.client.connect()
        await self.client.configure()

    @asynctest.skip
    async def test_publish_event(self):
        await self.client.publish.send_event(self.payload)

    async def test_channel_property(self):
        """The property only will change after configure()."""
        self.assertIsNone(self.client.channel)

    async def test_protocol_property(self):
        """The property only will change after configure()."""
        self.assertIsNone(self.client.protocol)
