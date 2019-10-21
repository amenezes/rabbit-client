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

    async def setUp(self):
        self.client = await rabbit_client(asyncio.get_event_loop())
        self.subscribe = await get_subscribe(self.client)
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    async def test_configure_subscribe_without_publish(self):
        await self.subscribe.configure()

    async def test_create_subscribe_with_publish(self):
        subscribe = Subscribe(
            client=self.client,
            publish=Publish(client=self.client)
        )
        self.assertIsInstance(subscribe.publish, Publish)

    async def test_subscribe_set_valid_publish(self):
        self.subscribe.publish = Publish(client=self.client)
        await self.subscribe.configure()

    async def test_subscribe_set_invalid_publish(self):
        with self.assertRaises(ValueError):
            self.subscribe.publish = None

    async def test_client_connect_on_subscribe(self):
        subscribe = Subscribe(AioRabbitClient())
        await subscribe.configure()

    async def test_reject_event(self):
        await self.subscribe.reject_event(EnvelopeMock())

    async def test_ack_event(self):
        await self.subscribe.ack_event(EnvelopeMock())
