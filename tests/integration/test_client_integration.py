import asyncio
import json

import asynctest

from tests.integration.setup import rabbit_client


class TestClientIntegration(asynctest.TestCase):

    async def setUp(self):
        self.client = await rabbit_client(asyncio.get_event_loop())
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    async def test_channel_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.channel)

    async def test_protocol_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.protocol)

    async def test_transport_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.transport)
    
    async def test_instances_property(self):
        self.client.instances = self
        self.client.instances = self
        self.assertEqual(len(self.client.instances), 1)
