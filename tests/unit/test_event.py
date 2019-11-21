import json
import unittest
from datetime import datetime

import attr

from rabbit.tlog.event import Event


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.payload = {
            'paginas': [{'corpo': 'abcd123'}],
            'documento': 123,
            'descricao': 'abc'
        }
        self.created_at = datetime.utcnow()
        self.event = Event(
            body=bytes(json.dumps(self.payload), 'utf-8'),
            created_at=self.created_at
        )
        self.event.id = 0

    def test_attributes(self):
        values = [
            bytes(json.dumps(self.payload), 'utf-8'),
            self.created_at
        ]
        for value in values:
            with self.subTest(value=value):
                self.assertIn(
                    value,
                    attr.asdict(self.event).values()
                )
