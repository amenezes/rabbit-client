import os

from cleo import Application, Command

from rabbit import __version__
from rabbit.cli.consumer import Consumer
from rabbit.cli.producer import Producer
from rabbit.cli.pubsub import PubSub


class PollingPublisherCommand(Command):
    """
    Start PollingPublisher sample application 📥📤

    polling-publisher
    """

    def handle(self):
        self.line(f"<info>>></info> <options=bold>starting polling-publisher...</>")
        pubsub = PubSub()
        try:
            pubsub.run()
        except KeyboardInterrupt:
            self.line(f"<info>!></info> <options=bold>polling-publisher finished!</>")
            raise SystemExit


class ConsumerCommand(Command):
    """
    Start a consumer sample application 📥

    consumer
    """

    def handle(self):
        self.line(f"<info>>></info> <options=bold>starting consumer...</>")
        consumer = Consumer()
        try:
            consumer.run()
        except KeyboardInterrupt:
            self.line(f"<info>!></info> <options=bold>consumer finished!</>")
            raise SystemExit


class EventCommand(Command):
    """
    Send a sample message 📨 to Consumer or PollingPublisher

    send-event
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
            prod = Producer(qtd=int(self.option("events")))
            prod.send_event()
            self.line(f"<info>!></info> <options=bold>event successfully submitted!</>")
        except OSError:
            self.line("<error>Failure to connect in rabbit.</error>")


application = Application("rabbit-client", f"{__version__}")
application.add(PollingPublisherCommand())
application.add(ConsumerCommand())
application.add(EventCommand())


if __name__ == "__main__":
    application.run()
