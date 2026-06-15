import asyncio
import logging

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


async def test_background_tasks_discard_removes_failed_task(background_tasks):
    async def failing_task():
        raise ValueError("task error")

    background_tasks.add("failing", failing_task)
    task = background_tasks["failing"]

    with pytest.raises(ValueError):
        await task

    assert "failing" not in background_tasks.tasks_by_name()


async def test_background_tasks_discard_logs_warning_on_failure(
    background_tasks, caplog
):
    async def failing_task():
        raise ValueError("task error")

    with caplog.at_level(logging.WARNING):
        background_tasks.add("failing", failing_task)

    task = background_tasks["failing"]
    with pytest.raises(ValueError):
        await task

    assert any("Task 'failing' failed" in r.message for r in caplog.records)
