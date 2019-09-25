import unittest

from rabbit.job import SampleJob


class TestJob(unittest.TestCase):

    def test_echo_job(self):
        self.assertIsInstance(
            SampleJob.echo_job(1, 2, 3, a=1, b=2),
            str
        )
