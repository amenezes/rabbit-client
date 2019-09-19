import unittest

from rabbit.exchange import Exchange


class TestExchange(unittest.TestCase):

    def setUp(self):
        self.exchange = Exchange(
            name='exchange',
            exchange_type='',
            topic='#'
        )

        def test_attributes(self):
            self.assertEqual(self.exchange, 'exchange')
            self.assertEqual(self.exchange_type, '')
            self.assertEqual(self.topic, 'topic')
