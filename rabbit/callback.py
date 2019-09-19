import asyncio
import logging

import aioamqp

from rabbit.event import Event
from rabbit.exchange import Exchange
# from rabbit.task import Task


logging.getLogger(__name__).addHandler(logging.NullHandler())


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
        # await self.task.execute()
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
    event = Event(
        channel=event.channel,
        payload=event.payload,
        exchange=Exchange(
            name=self.publish.dlx_exchange.name,
            exchange_type=self.publish.dlx_exchange.exchange_type,
            topic=self.publish.dlx_exchange.topic
        ),
        properties=event.properties,
        timeout=event.timeout * 5
    )
    await event.publish(self.subscribe.queue.name)
    await event.reject()
