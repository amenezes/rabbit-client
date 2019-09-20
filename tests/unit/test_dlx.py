import unittest

from rabbit.dlx import DLX
from rabbit.queue import Queue


class TestDLX(unittest.TestCase):

    def setUp(self):
        self.dlx = DLX(
            Queue(name='queue'),
            routing_key='queue'
        )
