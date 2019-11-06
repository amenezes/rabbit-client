import unittest

from rabbit.observer import Observer


class TestObserver(unittest.TestCase):

    def setUp(self):
        self.config_observer = Observer()

    def test_attach(self):
        self.config_observer.attach(list)

    def test_detach(self):
        self.config_observer.detach(list)

    def test_invalid_object_detach(self):
        self.config_observer.detach(dict)
