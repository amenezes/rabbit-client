import unittest

from rabbit.config import ConfigObserver


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config_observer = ConfigObserver()

    def test_attach(self):
        self.config_observer.attach(list)

    def test_detach(self):
        self.config_observer.detach(list)

    def test_invalid_object_detach(self):
        self.config_observer.detach(dict)
