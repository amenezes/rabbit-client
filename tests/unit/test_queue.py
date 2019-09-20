import unittest

import attr

from rabbit.queue import Queue


class TestQueue(unittest.TestCase):

    def setUp(self):
        self.queue = Queue(name='queue')

    def test_attributes(self):
        values = ['queue', True, {}]
        for value in values:
            with self.subTest(value=value):
                self.assertIn(
                    value,
                    attr.asdict(self.queue).values()
                )
