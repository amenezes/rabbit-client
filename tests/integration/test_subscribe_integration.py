import asyncio
import json

import asynctest

from rabbit.client import AioRabbitClient
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

    async def test_configure_subscribe(self):
        await self.subscribe.configure()

    async def test_client_connect_on_subscribe(self):
        subscribe = Subscribe(AioRabbitClient())
        await subscribe.configure()

    async def test_reject_event(self):
        await self.subscribe.reject_event(EnvelopeMock())

    async def test_ack_event(self):
        await self.subscribe.ack_event(EnvelopeMock())
