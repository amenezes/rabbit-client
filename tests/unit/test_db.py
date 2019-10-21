import unittest

from rabbit.tlog.db import DB


class TestDB(unittest.TestCase):

    def setUp(self):
        self.db = DB()

    def test_invalid_stmt_execute(self):
        with self.assertRaises(TypeError):
            self.db.execute('SELECT * FROM event')
