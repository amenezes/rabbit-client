import json

import asynctest

from rabbit.tlog.db import DB


class TestDB(asynctest.TestCase):

    def format_payload(self, payload):
        return bytes(json.dumps(payload), 'utf-8')

    def setUp(self):
        self.payload = {
            'paginas': [{'corpo': 'abcd123'}],
            'documento': 123,
            'descricao': 'abc'
        }
        self.db = DB()

    async def test_save(self):
        data = self.format_payload(self.payload)
        await self.db.save(data)
