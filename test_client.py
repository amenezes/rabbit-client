import asyncio
import logging

from aiohttp import web

from rabbit.client import AioRabbitClient
# from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.task import Task
from rabbit.tlog import echo_persist_job


async def handle_info(request):
    return web.json_response({'app': 'rabbit-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


def configure_default_client(app):
    client = AioRabbitClient(app=app.loop)
    # consumer = Subscribe(client, publish=Publish())
    consumer = Subscribe(
        client,
        task=Task(job=echo_persist_job)
    )
    app.loop.create_task(consumer.configure())
    app['rabbit_client'] = client


logging.getLogger().setLevel(logging.DEBUG)
loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
configure_default_client(app)
web.run_app(app, host='0.0.0.0', port=5000)
