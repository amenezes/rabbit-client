import asyncio
import json

import asynctest

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish
from rabbit.subscribe import Subscribe

from tests.integration.setup import (
    EnvelopeMock,
    get_subscribe,
    rabbit_client
)


class TestSubscribeIntegration(asynctest.TestCase):

    @asynctest.skip
    async def setUp(self):
        self.client = await rabbit_client(asyncio.get_event_loop())
        self.subscribe = await get_subscribe(self.client)
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    @asynctest.skip
    async def test_configure_subscribe_without_publish(self):
        await self.subscribe.configure()

    @asynctest.skip
    async def test_create_subscribe_with_publish(self):
        subscribe = Subscribe(client=self.client, publish=Publish())
        self.assertIsInstance(subscribe.publish, Publish)

    @asynctest.skip
    async def test_subscribe_set_valid_publish(self):
        self.subscribe.publish = Publish()
        await self.subscribe.configure()

    @asynctest.skip
    async def test_subscribe_set_invalid_publish(self):
        with self.assertRaises(ValueError):
            self.subscribe.publish = None

    @asynctest.skip
    async def test_client_connect_on_subscribe(self):
        subscribe = Subscribe(AioRabbitClient())
        await subscribe.configure()

    @asynctest.skip
    async def test_reject_event(self):
        await self.subscribe.reject_event(EnvelopeMock())

    @asynctest.skip
    async def test_ack_event(self):
        await self.subscribe.ack_event(EnvelopeMock())
