import unittest

from rabbit.job import echo_job


class TestSampleJob(unittest.TestCase):

    def setUp(self):
        self.payload = b'{"mykey": 123}'

    def test_sample_job_echo(self):
        self.assertIsInstance(echo_job(self.payload), bytes)
