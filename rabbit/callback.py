import logging

import attr

from rabbit.event import Event
from rabbit.task import Task


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s
class DefaultCallback:

    error_callback_action = attr.ib(validator=attr.validators.is_callable())
    task = attr.ib(
        type=Task,
        validator=attr.validators.is_callable()
    )
    subscribe = attr.ib(type=Subscribe)
    publish = attr.ib(type=Publish)

    async def reconnect_callback(self, exception):
        """Reconnect on RabbitMQ callback."""
        try:
            logging.error("Error to connect with message broker, a new attempt will occur in 10 seconds.")
            await asyncio.sleep(10)
            await self.error_callback_action()
        except aioamqp.exceptions.SynchronizationError:
            pass

    async def process_event_callback(self, channel, body, envelope, properties):
        try:
            await self.task.execute()
            event = Event(
                channel=channel,
                payload=body,
                properties=properties
            )
            event.ack()
            asyncio.sleep(5)
        except Exception as cause:
            await self.process_error_callback(cause, event)

    async def process_error_callback(self, exception_type, event):
        logging.error(f'Error to process the event: {exception_type}')
        timeout = await self.event.timeout()
        event = Event(
            channel=event.channel,
            payload=event.payload,
            exchange=Exchange(
                name=publish.dlx_exchange.name,
                exchange_type=publish.dlx_exchange.exchange_type,
                topic=publish.dlx_exchange.topic
            ),
            properties=properties,
            timeout=timeout*5
        )
        await event.publish(subscribe.queue.name)
        await event.reject()
