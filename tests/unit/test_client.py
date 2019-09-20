import unittest

from rabbit.client import AioRabbitClient


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = AioRabbitClient()
