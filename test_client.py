import asyncio

from aiohttp import web

from rabbit.client import AioRabbitClient


async def handle_info(request):
    return web.json_response({'app': 'aio-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


def configure(app):
    client = AioRabbitClient(app.loop)
    app.loop.run_until_complete(client.connect())
    # app.loop.run_until_complete(client.configure())
    app['rabbit_client'] = client


loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
configure(app)
# app.loop.call_soon(app['rabbit_client'], configure(app))
app.loop.run_until_complete(app['rabbit_client'].configure())
web.run_app(app, host='0.0.0.0', port=5000)
