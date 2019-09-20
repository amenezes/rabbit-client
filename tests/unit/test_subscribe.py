import unittest

from rabbit.subscribe import Subscribe


class TestSubscribe(unittest.TestCase):

    def setUp(self):
        self.subscribe = Subscribe()
