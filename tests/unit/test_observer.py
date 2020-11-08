import asyncio

import pytest


@pytest.mark.asyncio
@pytest.fixture
async def loop():
    try:
        loop = asyncio.get_running_loop()
    except AttributeError:
        loop = asyncio._get_running_loop()
    return loop


class MockObject:
    async def configure(self):
        pass


def test_attach(observer):
    observer.attach(list)
    assert list in observer


def test_attach_duplicated_object(observer):
    observer.attach(list)
    observer.attach(list)
    assert len(observer) == 1


def test_detach(observer):
    observer.detach(list)
    assert list not in observer


def test_invalid_object_detach(observer):
    result = observer.detach(dict)
    assert result is None


@pytest.mark.asyncio
async def test_notify_invalid(observer, loop):
    observer.notify(loop)


@pytest.mark.asyncio
async def test_notify(observer, loop):
    observer.attach(MockObject())
    observer.notify(loop)
