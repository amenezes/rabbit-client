import json

import asynctest

from rabbit.client import AioRabbitClient
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.tlog.db import DB


class TestPollingPublish(asynctest.TestCase):

    async def format_payload(self,
                             event_id,
                             event_body,
                             event_created_by,
                             event_status):
        return (event_id, event_body, event_created_by, event_status)

    async def setUp(self):
        self.raw_body = {
            'paginas': [{'corpo': 'abcd123'}],
            'documento': 123,
            'descricao': 'abc'
        }
        self.body = bytes(json.dumps(self.raw_body), 'utf-8')
        self.polling = PollingPublisher(
            DB(),
            Publish(client=AioRabbitClient())
        )
