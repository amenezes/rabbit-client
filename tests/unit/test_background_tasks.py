import asyncio

import pytest

from rabbit.background_tasks import BackgroundTasks
from rabbit.job import async_echo_job


@pytest.fixture
def background_tasks():
    return BackgroundTasks()


async def test_background_tasks_add(background_tasks):
    background_tasks.add("test-task", async_echo_job, b'{"message": "test"}')
    assert len(background_tasks) == 1


async def test_background_tasks_multiple_add(background_tasks):
    background_tasks.add("test-task-1", async_echo_job, b'{"message": "test"}')
    background_tasks.add("test-task-1", async_echo_job, b'{"message": "test"}')
    background_tasks.add("test-task-2", async_echo_job, b'{"message": "test2"}')
    assert len(background_tasks) == 2


async def test_background_tasks_by_name(background_tasks):
    background_tasks.add("test-task", async_echo_job, b'{"message": "test"}')
    for task in background_tasks:
        assert task.get_name() == "test-task"


async def test_background_tasks_getitem(background_tasks):
    background_tasks.add("test-task", async_echo_job, b'{"message": "test"}')
    assert isinstance(background_tasks["test-task"], asyncio.Task)


def test_background_tasks_len(background_tasks):
    assert len(background_tasks) == 0


def test_background_tasks_repr(background_tasks):
    assert repr(background_tasks) == "BackgroundTasks(tasks=0, tasks_by_name=[])"
