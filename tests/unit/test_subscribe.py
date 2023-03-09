import pytest

from rabbit.exceptions import ClientNotConnectedError
from tests.conftest import EnvelopeMock

PAYLOAD = b'{"a": 1}'


async def test_register_subscribe_without_client_connected(subscribe):
    with pytest.raises(ClientNotConnectedError):
        await subscribe.configure()


async def test_reject_event(subscribe_mock):
    await subscribe_mock.reject_event(EnvelopeMock())


async def test_ack_event(subscribe_mock):
    await subscribe_mock.ack_event(EnvelopeMock())


def test_subscribe_repr(subscribe_mock):
    assert isinstance(repr(subscribe_mock), str)


async def test_nack_event(subscribe_mock):
    await subscribe_mock.nack_event(EnvelopeMock())
