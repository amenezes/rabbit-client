import asyncio

import pytest
from click.testing import CliRunner

from rabbit.cli import consumer, send_event
from rabbit.cli.consumer import Consumer
from rabbit.client import AioRabbitClient
from rabbit.subscribe import Subscribe


@pytest.fixture(scope="session")
def cli_runner():
    return CliRunner()


def test_consumer_command(cli_runner, monkeypatch):
    async def fail_connect(self, *a, **kw):
        raise OSError("Connection refused")

    monkeypatch.setattr(AioRabbitClient, "connect", fail_connect)

    result = cli_runner.invoke(consumer, [])
    assert result.exit_code == 1


def test_send_event_missing_payload(cli_runner):
    result = cli_runner.invoke(send_event, [])
    assert result.exit_code == 2


async def test_consumer_connects_and_configures(monkeypatch):
    connect_called = False
    configure_called = False

    async def mock_connect(self, **kwargs):
        nonlocal connect_called
        connect_called = True

    async def mock_configure(self, channel=None):
        nonlocal configure_called
        configure_called = True

    async def mock_channel(self):
        return None

    monkeypatch.setattr(AioRabbitClient, "connect", mock_connect)
    monkeypatch.setattr(AioRabbitClient, "channel", mock_channel)
    monkeypatch.setattr(Subscribe, "configure", mock_configure)

    consumer = Consumer(
        "localhost",
        5672,
        "guest",
        "guest",
        "exchange_test",
        "topic",
        "#",
        "queue_test",
        1,
    )

    task = asyncio.create_task(consumer._run(task=lambda msg: None, verbose=False))
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert connect_called
    assert configure_called
