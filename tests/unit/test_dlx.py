import unittest

from rabbit.dlx import DLX
from rabbit.queue import Queue


class TestDLX(unittest.TestCase):

    def setUp(self):
        self.dlx = DLX(
            Queue(name='queue'),
            routing_key='queue'
        )

    def test_ensure_endswith_dlq(self):
        values = {
            'queue': 'queue.dlq',
            'queue.dlq': 'queue.dlq',
            'a.b.c': 'a.b.c.dlq'
        }
        for value in values.keys():
            with self.subTest(value=value):
                self.assertEqual(
                    self.dlx._ensure_endswith_dlq(value),
                    values.get(value)
                )

    # def test_dlq_properties(self):
    #     self.assertIsInstance(
    #         self.dlx._get_properties(
    #             10000,
    #             'Test exception',
    #             'test_exchange',
    #             '#'
    #         ),
    #         dict
    #     )
