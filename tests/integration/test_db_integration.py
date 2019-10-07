import unittest

from rabbit.tlog.db import DB


class TestDB(unittest.TestCase):

    def setUp(self):
        self.db = DB()

    def test_db_configure(self):
        self.db.configure()
