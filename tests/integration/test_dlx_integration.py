import asyncio
import json

import asynctest

from rabbit.exceptions import OperationError

from tests.integration.setup import (
    EnvelopeMock,
    PropertiesMock,
    get_dlx,
    rabbit_client
)


class TestDLXIntegration(asynctest.TestCase):

    async def setUp(self):
        self.client = await rabbit_client(asyncio.get_event_loop())
        self.dlx = await get_dlx(self.client)
        self.payload = bytes(
            json.dumps({"message": "aiorabbitclient test."}),
            'utf-8'
        )

    async def test_dlx_send_event(self):
        await self.dlx.send_event(
            Exception('test'),
            self.payload,
            EnvelopeMock(),
            PropertiesMock()
        )

    async def test_invalid_delay_on_dlx_send_event(self):
        await self.dlx.send_event(
            Exception('test'),
            self.payload,
            EnvelopeMock(),
            PropertiesMock(headers=None)
        )

    @asynctest.skip
    async def test_invalid_client_on_dlx(self):
        dlx = await get_dlx(None)
        with self.assertRaises(OperationError):
            await dlx.configure()

    async def test_configure_dlx(self):
        await self.dlx.configure()
