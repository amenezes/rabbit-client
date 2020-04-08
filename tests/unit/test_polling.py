import pytest

from conftest import DBMock
from rabbit.polling import PollingPublisher
from rabbit.tlog.event import Event


def test_format_payload(polling_mock):
    result = polling_mock._format_payload(Event(b'{"key": "value"}'))
    assert result is not None


@pytest.mark.asyncio
async def test_non_retrieve_event(publish_mock):
    polling = PollingPublisher(publish_mock, DBMock())
    await polling._retrieve_event()


@pytest.mark.asyncio
async def test_retrieve_event_to_send(publish_mock):
    polling = PollingPublisher(publish_mock, DBMock(True))
    await polling._retrieve_event()
