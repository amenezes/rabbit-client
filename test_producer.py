import asyncio

from rabbit.client import AioRabbitClient


loop = asyncio.get_event_loop()

r = AioRabbitClient()
loop.run_until_complete(r.connect())