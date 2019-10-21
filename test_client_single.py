import asyncio
import logging
import os

from aiohttp import web

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish
from rabbit.polling import PollingPublisher
from rabbit.queue import Queue
from rabbit.exchange import Exchange
from rabbit.subscribe import Subscribe
from rabbit.task import Task
from rabbit.tlog import echo_persist_job
from rabbit.tlog.db import DB


async def handle_info(request):
    return web.json_response({'app': 'aio-rabbit-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


def configure_default_client(app):
    client1 = AioRabbitClient(app=app.loop)
    app.loop.create_task(client1.persistent_connect())
    consumer = Subscribe(
        client1,
        task=Task(job=echo_persist_job)
    )
    app.loop.create_task(consumer.configure())

    # polling-publisher
    client2 = AioRabbitClient(app=app.loop)
    app.loop.create_task(client2.persistent_connect())
    app.loop.run_until_complete(asyncio.sleep(2))
    publish = Publish(
        client2,
        exchange=Exchange(
            name=os.getenv('PUBLISH_EXCHANGE', 'default.out.exchange'),
            exchange_type=os.getenv('PUBLISH_EXCHANGE_TYPE', 'topic'),
            topic=os.getenv('PUBLISH_TOPIC', '#')
        ),
        queue=Queue(
            name=os.getenv('PUBLISH_QUEUE', 'default.publish.queue')
        )
    )
    polling = PollingPublisher(
        publish=publish,
        db=DB(driver='postgresql://postgres:postgres@postgres:5432/db')
    )
    app.loop.create_task(publish.configure())
    app.loop.create_task(polling.run())


logging.getLogger().setLevel(logging.DEBUG)
loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
configure_default_client(app)
web.run_app(app, host='0.0.0.0', port=5000)