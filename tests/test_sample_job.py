import unittest

from rabbit.job import SampleJob


class TestSampleJob(unittest.TestCase):

    def test_sample_job_echo(self):
        self.assertIsInstance(SampleJob.echo_job(), dict)
