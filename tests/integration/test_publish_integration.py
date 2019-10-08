import asyncio
import json

import asynctest

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish

from tests.integration.setup import get_publish, rabbit_client


class TestPublishIntegration(asynctest.TestCase):

    @asynctest.skip
    async def setUp(self):
        client = await rabbit_client(asyncio.get_event_loop())
        self.publish = await get_publish(client)
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    @asynctest.skip
    async def test_publish_event(self):
        self.assertEqual(len(self.publish.client.instances), 3)
        # await self.publish.send_event(self.payload)

    @asynctest.skip
    async def test_configure_publish(self):
        await self.publish.configure()

    @asynctest.skip
    async def test_client_connect_on_publish(self):
        publish = Publish(AioRabbitClient())
        await publish.configure()
