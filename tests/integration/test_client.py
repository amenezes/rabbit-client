import asyncio
import json

from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

import asynctest

from rabbit.client import AioRabbitClient


class EnvelopeMock(Envelope):

    def __init__(self):
        pass

    @property
    def exchange_name(self):
        return 'src-exchange'

    @property
    def routing_key(self):
        return '#'


class PropertiesMock(Properties):

    def __init__(self, headers={'x-delay': 5000}):
        self.headers = headers


class TestClient(asynctest.TestCase):

    async def _get_rabbit_client(self, loop):
        client = AioRabbitClient(app=loop)
        await client.connect()
        await client.configure()
        return client

    async def setUp(self):
        loop = asyncio.get_event_loop()
        self.client = await self._get_rabbit_client(loop)
        self.payload = {"message": "aiorabbitclient test."}

    async def test_publish_event(self):
        await self.client.publish.send_event(
            bytes(json.dumps(self.payload), 'utf-8')
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

    async def test_dlx_send_event(self):
        await self.client.subscribe.dlx.send_event(
            Exception('test'),
            bytes(json.dumps(self.payload), 'utf-8'),
            EnvelopeMock(),
            PropertiesMock()
        )

    async def test_invalid_delay_on_dlx_send_event(self):
        await self.client.subscribe.dlx.send_event(
            Exception('test'),
            bytes(json.dumps(self.payload), 'utf-8'),
            EnvelopeMock(),
            PropertiesMock(headers=None)
        )
