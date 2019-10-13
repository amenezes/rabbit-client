import json
import unittest

from rabbit.tlog.db import DB
from rabbit.tlog.event_persist import EventPersist


class TestEventPersist(unittest.TestCase):

    def format_payload(self, payload):
        return bytes(json.dumps(payload), 'utf-8')

    def setUp(self):
        self.payload = {
            'paginas': [{'corpo': 'abcd123'}],
            'documento': 123,
            'descricao': 'abc'
        }
        self.event_persist = EventPersist()

    def test_valid_payload(self):
        payload = self.format_payload(self.payload)
        self.assertIsNone(
            self.event_persist.save(payload)
        )

    def test_invalid_payload(self):
        with self.assertRaises(TypeError):
            self.event_persist.save(self.payload)

    def test_get_db_connection(self):
        db = self.event_persist._get_db_connection()
        self.assertIsInstance(db, DB)

    def test_get_db_connection_singleton(self):
        db1 = self.event_persist._get_db_connection()
        db2 = self.event_persist._get_db_connection()
        self.assertEqual(id(db1), id(db2))

    def test_save(self):
        data = self.format_payload(self.payload)
        self.event_persist.save(data)
