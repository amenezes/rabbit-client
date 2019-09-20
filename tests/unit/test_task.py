import unittest

from rabbit.task import Task


class TestTask(unittest.TestCase):

    def setUp(self):
        self.task = Task()
