import asyncio
import logging
import os

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.queue import Queue


logging.getLogger().setLevel(logging.DEBUG)
loop = asyncio.get_event_loop()

publish = Publish(
    AioRabbitClient(loop),
    exchange=Exchange(
        name=os.getenv('PUBLISH_EXCHANGE', 'default.out.exchange'),
        exchange_type=os.getenv('PUBLISH_EXCHANGE_TYPE', 'topic'),
        topic=os.getenv('PUBLISH_TOPIC', '#')
    ),
    queue=Queue(
        name=os.getenv('PUBLISH_QUEUE', 'default.publish.queue')
    )
)
loop.run_until_complete(publish.configure())
polling = PollingPublisher(publish)
# loop.run_until_complete(polling.configure())
print(
    "[>] Starting polling job..."
)

while True:
    loop.run_until_complete(asyncio.sleep(5))
    loop.run_until_complete(
        polling.run()
    )