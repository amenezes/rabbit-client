import logging
import os
import sys
from pathlib import Path

from cleo import Application, Command
from rich.live import Live
from rich.logging import RichHandler

from rabbit import __version__
from rabbit.cli import Consumer, Publisher


class ConsumerCommand(Command):
    """
    Start a consumer sample application 📥

    consumer
        {chaos? : enable chaos mode. Raise random Exception to test DLX mechanism.}
        {--c|concurrent=1 : concurrent events to process.}
        {--x|exchange=default.in.exchange : exchange name.}
        {--t|type=topic : exchange topic type name.}
        {--k|key=# : exchange topic key.}
        {--f|queue=default.subscribe.queue : queue name.}
    """

    def handle(self):
        logging.basicConfig(
            level="NOTSET",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(show_path=False)],
        )
        with Live(refresh_per_second=1, auto_refresh=False) as live:
            live.console.print("Running consumer...")
            consumer = Consumer(
                exchange_name=os.getenv(
                    "SUBSCRIBE_EXCHANGE_NAME", self.option("exchange")
                ),
                exchange_type=os.getenv("SUBSCRIBE_EXCHANGE_TYPE", self.option("type")),
                exchange_topic=os.getenv("SUBSCRIBE_TOPIC", self.option("key")),
                queue_name=os.getenv("SUBSCRIBE_QUEUE_NAME", self.option("queue")),
                concurrent=int(self.option("concurrent")),
            )
            try:
                consumer.run(self.argument("chaos"))
            except KeyboardInterrupt:
                self.line("<info>!></info> <options=bold>consumer finished!</>")
                raise SystemExit


class EventCommand(Command):
    """
    Send a sample message 📨 to Consumer or PollingPublisher

    send-event
        {payload : payload file in json format.}
        {--e|events=1 : qtd events to send.}
        {--x|exchange=default.in.exchange : exchange name.}
        {--k|key=# : exchange topic key.}
        {--host=localhost : rabbit hostname.}
        {--port=5672 : rabbit port.}
        {--login=guest : rabbit login.}
        {--password=guest : rabbit password.}
        {--ssl : enable rabbit ssl connection.}
        {--verify : verify ssl certificate?.}
        {--channels=1 : channel max.}
    """

    def handle(self):
        if self.io.verbosity:
            self.line(
                f"<info>>></info> <options=bold>"
                f"[exchange: {os.getenv('PUBLISH_EXCHANGE_NAME', self.option('exchange'))}"
                f" | key: {os.getenv('PUBLISH_ROUTING_KEY', self.option('key'))}"
                f" | events: {self.option('events')}]</>"
            )
        if not Path(f"{self.argument('payload')}").exists():
            self.line(f"<error>File not found: {self.argument('payload')}</error>")
            sys.exit(1)
        payload = Path(f"{self.argument('payload')}").read_bytes()
        try:
            prod = Publisher(
                payload,
                qtd=int(self.option("events")),
                exchange_name=os.getenv(
                    "PUBLISH_EXCHANGE_NAME", self.option("exchange")
                ),
                routing_key=os.getenv("PUBLISH_ROUTING_KEY", self.option("key")),
                host=self.option("host"),
                port=self.option("port"),
                login=self.option("login"),
                password=self.option("password"),
                ssl=self.option("ssl"),
                verify_ssl=self.option("verify"),
                channel_max=int(self.option("channels")),
            )
            prod.send_event()
            self.line("<info>!></info> <options=bold>event successfully submitted!</>")
        except OSError:
            self.line("<error>Failure to connect to RabbitMQ.</error>")


application = Application("rabbit-client", f"{__version__}")
application.add(ConsumerCommand())
application.add(EventCommand())


if __name__ == "__main__":
    application.run()
