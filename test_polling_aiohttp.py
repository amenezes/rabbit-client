import asyncio
import logging
import os

from aiohttp import web

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
polling = PollingPublisher(publish)


def configure_polling_publisher(app, polling, publish):
    app.loop.run_until_complete(publish.configure())
    app.loop.create_task(asyncio.sleep(60))
    app.loop.create_task(polling.run())


# loop.run_until_complete(polling.configure())
print(
    "[>] Starting polling job..."
)
app = web.Application(loop=loop)
configure_polling_publisher(app, polling, publish)
web.run_app(app, host='0.0.0.0', port=5002)
# app.loop.run_until_complete(publish.configure())
# app.loop.run_until_complete(polling.run())
# while True:
#     loop.run_until_complete(asyncio.sleep(60))
# loop.run_until_complete(polling.run())
