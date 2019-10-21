import asynctest

from rabbit.client import AioRabbitClient
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event


class ResponseMock:
    def first(self):
        return (1, b'123', False)


class DBMock(DB):
    value = False

    def __init__(self, value=False):
        self.value = value

    def execute(self, value):
        if self.value:
            return ResponseMock()
        return False


class TestPollingPublisher(asynctest.TestCase):

    async def setUp(self):
        self.publish = Publish(client=AioRabbitClient())
        self.polling = PollingPublisher(self.publish)

    async def test_assemble_event(self):
        result = await self.polling._assemble_event((1, b'teste', False))
        self.assertIsInstance(result, Event)

    async def test_retrieve_valid_event(self):
        polling = PollingPublisher(
            publish=self.publish, db=DBMock(True)
        )
        response = await polling._retrieve_event()
        self.assertIsNotNone(response)

    async def test_retrieve_nothing(self):
        polling = PollingPublisher(
            publish=self.publish, db=DBMock()
        )
        response = await polling._retrieve_event()
        self.assertIsNone(response)

    async def test_update_event_status(self):
        polling = PollingPublisher(
            publish=self.publish, db=DBMock()
        )
        await polling._update_event_status(
            Event(b'event mock', 1)
        )
