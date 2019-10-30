import asyncio
import logging
import os

from aiohttp import web

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.polling import PollingPublisher
from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.queue import Queue
from rabbit.tlog.event_persist import EventPersist


logging.getLogger().setLevel(logging.DEBUG)
loop = asyncio.get_event_loop()

# consumer
subscribe_client = AioRabbitClient(loop)
loop.create_task(subscribe_client.persistent_connect())
subscribe = Subscribe(
    client=subscribe_client,
    persist=EventPersist()
)

# polling-publisher
polling_client = AioRabbitClient(loop)
loop.create_task(polling_client.persistent_connect())
publish = Publish(
    polling_client,
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


def configure_polling_publisher(app, polling, publish, subscribe):
    app.loop.run_until_complete(publish.configure())
    app.loop.run_until_complete(subscribe.configure())
    app.loop.create_task(asyncio.sleep(60))
    app.loop.create_task(polling.run())


print(
    "[>] Starting polling job..."
)
app = web.Application(loop=loop)
configure_polling_publisher(app, polling, publish, subscribe)
web.run_app(app, host='0.0.0.0', port=5002)
