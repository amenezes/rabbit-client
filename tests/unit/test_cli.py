import asyncio

import pytest
from cleo import CommandTester

from rabbit.__main__ import application
from rabbit.cli.consumer import Consumer
from rabbit.exceptions import AttributeNotInitialized
from rabbit.job import async_echo_job


def test_consumer_command():
    command = application.find("consumer")
    ct = CommandTester(command)
    assert ct.io.fetch_output() is not None


def test_file_not_found_event_command():
    command = application.find("send-event")
    ct = CommandTester(command)
    with pytest.raises(SystemExit):
        ct.execute("xxx")


def test_consumer_connection_error():
    consumer = Consumer("exchange_test", "topic", "#", "queue_test", 1)
    loop = asyncio.get_event_loop()
    with pytest.raises(AttributeNotInitialized):
        loop.run_until_complete(consumer.init(async_echo_job))
