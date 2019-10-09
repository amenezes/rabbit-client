import asyncio
import json

import asynctest

from tests.integration.setup import rabbit_client


class TestClientIntegration(asynctest.TestCase):

    @asynctest.skip
    async def setUp(self):
        self.client = await rabbit_client(asyncio.get_event_loop())
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    @asynctest.skip
    async def test_channel_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.channel)

    @asynctest.skip
    async def test_protocol_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.protocol)

    @asynctest.skip
    async def test_transport_property(self):
        """The property only will change after configure()."""
        self.assertIsNotNone(self.client.transport)

    @asynctest.skip
    async def test_instances_property(self):
        self.client.instances = self
        self.client.instances = self
        self.assertEqual(len(self.client.instances), 1)
