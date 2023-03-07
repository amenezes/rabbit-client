import pytest
from click.testing import CliRunner

from rabbit.cli import consumer, send_event
from rabbit.cli.consumer import Consumer
from rabbit.exceptions import AttributeNotInitialized
from rabbit.job import async_echo_job


@pytest.fixture(scope="session")
def cli_runner():
    return CliRunner()


def test_consumer_command(cli_runner):
    result = cli_runner.invoke(consumer, [])
    assert result.exit_code == 1


def test_file_not_found_event_command(cli_runner):
    result = cli_runner.invoke(send_event, [])
    result.exit_code == 1


async def test_consumer_connection_error():
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
    with pytest.raises(AttributeNotInitialized):
        await consumer.init(async_echo_job)
