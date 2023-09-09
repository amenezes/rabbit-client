import logging
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from trogon import tui

from rabbit import __version__
from rabbit.cli.consumer import Consumer
from rabbit.cli.publisher import Publisher

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
)
console = Console()


@tui(command="terminal-ui", help="Open terminal UI")
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.option(
    "--host",
    default="localhost",
    show_default=True,
    help="RabbitMQ hostname.",
)
@click.option(
    "--port",
    default="5672",
    show_default=True,
    help="RabbitMQ port.",
)
@click.option(
    "--login",
    default="guest",
    show_default=True,
    help="RabbitMQ username.",
)
@click.option(
    "--password",
    default="guest",
    show_default=True,
    help="RabbitMQ username.",
)
@click.option(
    "-c",
    "--concurrent",
    default=1,
    show_default=True,
    help="How many concurrent events to process.",
)
@click.option(
    "-x",
    "--exchange",
    default="default.in.exchange",
    envvar="SUBSCRIBE_EXCHANGE_NAME",
    show_default=True,
    help="Exchange name.",
)
@click.option(
    "-t",
    "--type",
    default="topic",
    envvar="SUBSCRIBE_EXCHANGE_TYPE",
    show_default=True,
    help="Exchange topic type name.",
)
@click.option(
    "-k",
    "--key",
    default="#",
    envvar="SUBSCRIBE_TOPIC",
    show_default=True,
    help="Exchange topic key.",
)
@click.option(
    "-q",
    "--queue",
    default="default.subscribe.queue",
    envvar="SUBSCRIBE_QUEUE_NAME",
    show_default=True,
    help="Queue name.",
)
@click.option(
    "--chaos",
    is_flag=True,
    help="Enable chaos mode. Raise random Exception to test DLX mechanism.",
)
@click.option("-v", "--verbose", is_flag=True, help="Extend output info.")
def consumer(
    host, port, login, password, concurrent, exchange, type, key, queue, chaos, verbose
):
    """Start a consumer sample application 📩"""
    if verbose:
        table = Table.grid(padding=(0, 1))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="magenta")

        table.add_row("connection[yellow]:[/yellow] ", f"{login}:***@{host}:{port}")
        table.add_row("exchange[yellow]:[/yellow] ", exchange)
        table.add_row("type[yellow]:[/yellow] ", type)
        table.add_row("key[yellow]:[/yellow] ", key)
        table.add_row("queue[yellow]:[/yellow] ", queue)
        table.add_row("concurrent[yellow]:[/yellow] ", str(concurrent))
        table.add_row("chaos mode[yellow]:[/yellow] ", str(chaos))
        table.add_row("UI[yellow]:[/yellow] ", "http://localhost:15672")

        console.print(
            Panel(
                table,
                title="[bold yellow]consumer options[/bold yellow]",
                border_style="yellow",
                expand=True,
            )
        )

    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(show_path=False)],
    )
    with Live(refresh_per_second=1, auto_refresh=False) as live:
        live.console.print("🚀 Running consumer...")
        consumer = Consumer(
            host=host,
            port=port,
            login=login,
            password=password,
            exchange_name=exchange,
            exchange_type=type,
            exchange_topic=key,
            queue_name=queue,
            concurrent=concurrent,
        )
        try:
            consumer.run(chaos, verbose)
        except KeyboardInterrupt:
            console.print("🛑 [bold]Consumer successfully completed![bold]")
        except Exception as err:
            raise click.ClickException(f"💥 {err}")


@cli.command()
@click.argument(
    "payload",
    type=click.Path(
        exists=True,
        dir_okay=True,
        writable=False,
        readable=True,
        executable=False,
        path_type=Path,
    ),
)
@click.option(
    "-e",
    "--events",
    default=1,
    show_default=True,
    help="How many events to send.",
)
@click.option(
    "-x",
    "--exchange",
    envvar="PUBLISH_EXCHANGE_NAME",
    default="default.in.exchange",
    show_default=True,
    help="Exchange name.",
)
@click.option(
    "-k",
    "--key",
    envvar="PUBLISH_ROUTING_KEY",
    default="#",
    show_default=True,
    help="Exchange topic key.",
)
@click.option("--host", default="localhost", show_default=True, help="RabbitMQ host.")
@click.option("--port", default=5672, show_default=True, help="RabbitMQ port.")
@click.option("--login", default="guest", show_default=True, help="RabbitMQ login.")
@click.option(
    "--password", default="guest", show_default=True, help="RabbitMQ password."
)
@click.option(
    "--ssl",
    is_flag=True,
    default=False,
    show_default=True,
    help="Enable rabbit ssl connection.",
)
@click.option("--verify", is_flag=True, default=False, help="Verify ssl certificate?")
@click.option("--channels", default=1, show_default=True, help="Channel max.")
@click.option("-v", "--verbose", is_flag=True, help="Extend output info.")
def send_event(
    payload,
    events,
    exchange,
    key,
    host,
    port,
    login,
    password,
    ssl,
    verify,
    channels,
    verbose,
):
    """Send a sample message 📤 to Consumer or PollingPublisher"""
    if verbose:
        table = Table.grid(padding=(0, 1))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="magenta")

        table.add_row(
            "amqp_URI[yellow]:[/yellow] ", f"amqp://{login}:***@{host}:{port}"
        )
        table.add_row("exchange[yellow]:[/yellow] ", exchange)
        table.add_row("key[yellow]:[/yellow] ", key)
        table.add_row("events[yellow]:[/yellow] ", f"{events}")

        console.print(
            Panel(
                table,
                title="[bold yellow]sender options[/bold yellow]",
                border_style="yellow",
                expand=True,
            )
        )

    try:
        publish = Publisher(
            exchange_name=exchange,
            routing_key=key,
            host=host,
            port=port,
            login=login,
            password=password,
            ssl=ssl,
            verify_ssl=verify,
            channel_max=channels,
        )
        if payload.is_file():
            publish.send_event(payload.read_bytes(), events, payload.name)
        elif payload.is_dir():
            for f in payload.glob("*.json"):
                publish.send_event(f.read_bytes(), events, f.name)

    except OSError:
        raise click.ClickException("💥 Failure to connect to RabbitMQ!")
