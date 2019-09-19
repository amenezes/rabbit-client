import unittest

from rabbit.exchange import Exchange

import attr


class TestExchange(unittest.TestCase):

    def setUp(self):
        self.exchange = Exchange(
            name='exchange',
            exchange_type='topic',
            topic='#'
        )

    def test_attributes(self):
        values = ['exchange', 'topic', '#']
        for value in values:
            with self.subTest(value=value):
                self.assertIn(
                    value,
                    attr.asdict(self.exchange).values()
                )
