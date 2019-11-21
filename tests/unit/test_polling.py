import asynctest

from rabbit.client import AioRabbitClient
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.tlog.db import DB
from rabbit.tlog.event import Event


class DBMock(DB):
    value = False

    def __init__(self, value=False):
        self.value = value

    async def exec(self, stmt, params={}):
        pass

    async def get_oldest_event(self):
        if self.value:
            return Event(body=b'test')


class TestPollingPublisher(asynctest.TestCase):

    async def setUp(self):
        self.publish = Publish(client=AioRabbitClient())
        self.polling = PollingPublisher(DB(), self.publish)

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
