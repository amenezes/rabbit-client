import threading

import pytest


@pytest.mark.parametrize(
    "attr",
    [
        "cli",
        "console",
        "CONTEXT_SETTINGS",
        "Consumer",
        "Publisher",
        "consumer",
        "send_event",
    ],
)
def test_cli_module_attributes(attr):
    import rabbit.cli

    assert hasattr(rabbit.cli, attr)


def test_cli_thread_import():
    result = {}

    def import_in_thread():
        try:
            from rabbit.cli import Consumer, Publisher

            result.update(
                {"success": True, "consumer": Consumer, "publisher": Publisher}
            )
        except RuntimeError as e:
            result.update({"error": str(e), "success": False})

    thread = threading.Thread(target=import_in_thread)
    thread.start()
    thread.join()

    assert result["success"]
    assert result["consumer"] is not None
    assert result["publisher"] is not None


def test_cli_types():
    from rabbit.cli import cli, Consumer, Publisher, consumer, send_event, console

    import click
    from rich.console import Console

    assert isinstance(cli, click.Group)
    assert callable(consumer)
    assert callable(send_event)
    assert isinstance(Consumer, type)
    assert isinstance(Publisher, type)
    assert isinstance(console, Console)


def test_cli_singleton():
    import rabbit.cli as cli1
    import rabbit.cli as cli2

    assert cli1.cli is cli2.cli
    assert cli1.console is cli2.console
    assert cli1.CONTEXT_SETTINGS is cli2.CONTEXT_SETTINGS
    assert cli1.Consumer is cli2.Consumer
    assert cli1.Publisher is cli2.Publisher
