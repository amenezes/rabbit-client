import asyncio

from rabbit import logger
from rabbit.client import AioRabbitClient
from rabbit.job import async_echo_job, dlx_job
from rabbit.subscribe import Subscribe


class Consumer:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.subscribe_client = AioRabbitClient()
        self.loop.create_task(self.subscribe_client.persistent_connect())

    async def init(self, task):
        await asyncio.sleep(1)
        logger.info(f"Using {task.__doc__}")
        subscribe = Subscribe(
            client=self.subscribe_client,
            task=task,
        )
        await subscribe.configure()

    def run(self, dlx_task: bool = False):
        task = async_echo_job
        if dlx_task:
            task = dlx_job  # type: ignore
        self.loop.run_until_complete(self.init(task))
        self.loop.run_forever()
