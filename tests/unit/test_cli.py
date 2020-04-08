from cleo import CommandTester

from rabbit.__main__ import application


def test_polling_publisher_command():
    command = application.find("polling-publisher")
    ct = CommandTester(command)
    # ct.execute("-h")
    assert "" == ct.io.fetch_output()


def test_consumer_command():
    command = application.find("consumer")
    ct = CommandTester(command)
    # ct.execute("-h")
    assert "" == ct.io.fetch_output()


def test_event_command():
    command = application.find("send-event")
    ct = CommandTester(command)
    # ct.execute("-h")
    assert "" == ct.io.fetch_output()
