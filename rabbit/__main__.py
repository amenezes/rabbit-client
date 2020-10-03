import logging
import os
import sys

from cleo import Application, Command

from rabbit import __version__
from rabbit.cli import Consumer, Producer

logging.basicConfig(level=logging.INFO)


class ConsumerCommand(Command):
    """
    Start a consumer sample application 📥

    consumer
    """

    def handle(self):
        self.line("<info>>></info> <options=bold>starting consumer...</>")
        consumer = Consumer()
        try:
            consumer.run()
        except KeyboardInterrupt:
            self.line("<info>!></info> <options=bold>consumer finished!</>")
            raise SystemExit


class EventCommand(Command):
    """
    Send a sample message 📨 to Consumer or PollingPublisher

    send-event
        {payload : payload file in json format.}
        {--e|events=1 : events to send.}
    """

    def handle(self):
        self.line(
            f"<info>>></info> <options=bold>sending event to: "
            f"[exchange: {os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange')}"
            f" | topic: {os.getenv('SUBSCRIBE_TOPIC', '#')} | "
            f"subscribe: {os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')}]</>"
        )
        try:
            with open(f"{self.argument('payload')}", "rb") as f:
                payload = f.read()
        except FileNotFoundError:
            self.line(f"<error>File not found: {self.argument('payload')}</error>")
            sys.exit(1)
        try:
            prod = Producer(payload, qtd=int(self.option("events")))
            prod.send_event()
            self.line("<info>!></info> <options=bold>event successfully submitted!</>")
        except OSError:
            self.line("<error>Failure to connect to RabbitMQ.</error>")


application = Application("rabbit-client", f"{__version__}")
application.add(ConsumerCommand())
application.add(EventCommand())


if __name__ == "__main__":
    application.run()
