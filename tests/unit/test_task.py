import asynctest

from rabbit.task import Task


class TestTask(asynctest.TestCase):

    def setUp(self):
        self.task = Task()

    async def test_calling_invalid_job(self):
        custom_task = Task(job=None)
        with self.assertRaises(TypeError):
            await custom_task.execute()
