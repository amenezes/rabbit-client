import unittest

from rabbit.publish import Publish


class TestPublish(unittest.TestCase):

    def setUp(self):
        self.publish = Publish()
