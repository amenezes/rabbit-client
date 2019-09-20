import asyncio
import logging

from aiohttp import web

from rabbit.client import AioRabbitClient


async def handle_info(request):
    return web.json_response({'app': 'aio-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


async def configure(app):
    client = AioRabbitClient()
    app.loop.create_task(client.connect())
    app.loop.create_task(client.configure())


async def shutdown_server(app):
    app.loop.close()


app = web.Application()
app.on_startup.append(configure)
app.on_shutdown.append(shutdown_server)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
web.run_app(app, host='0.0.0.0', port=5000)
