import asyncio
import logging

from aiohttp import web

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish
from rabbit.subscribe import Subscribe
from rabbit.task import Task


def custom_job(*args, **kwargs):
    logging.info('Executing custom job.')
    return 'Custom JOB.'


async def handle_info(request):
    return web.json_response({'app': 'aio-rabbit-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


def configure_custom_client(app):
    client = AioRabbitClient(
        app=app.loop,
        subscribe=Subscribe(
            task=Task(job=custom_job),
            publish=Publish()
        )
    )
    app.loop.run_until_complete(client.connect())
    app.loop.create_task(client.configure())
    app['rabbit_client'] = client


def configure_default_client(app):
    # client = AioRabbitClient(app.loop) # console only output
    client = AioRabbitClient(
        app=app.loop,
        subscribe=Subscribe(
            publish=Publish()
        )
    )
    app.loop.run_until_complete(client.connect())
    app.loop.create_task(client.configure())
    app['rabbit_client'] = client


logging.getLogger().setLevel(logging.INFO)
loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
configure_default_client(app)
# configure_custom_client(app)
web.run_app(app, host='0.0.0.0', port=5000)
