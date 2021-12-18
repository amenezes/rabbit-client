import asyncio

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.job import async_chaos_job, async_echo_job
from rabbit.logger import logger
from rabbit.queue import Queue
from rabbit.subscribe import Subscribe


class Consumer:
    def __init__(
        self,
        exchange_name: str,
        exchange_type: str,
        exchange_topic: str,
        queue_name: str,
        concurrent: int,
    ):
        self.loop = asyncio.get_event_loop()
        self.subscribe_client = AioRabbitClient()
        self.loop.create_task(self.subscribe_client.persistent_connect())
        self.exchange_type = exchange_type
        self.exchange_topic = exchange_topic
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.concurrent = concurrent

    async def init(self, task):
        await asyncio.sleep(1)
        logger.info(f"Using {task.__doc__}")
        subscribe = Subscribe(
            client=self.subscribe_client,
            task=task,
            exchange=Exchange(
                self.exchange_name, self.exchange_type, self.exchange_topic
            ),
            queue=Queue(name=self.queue_name),
            concurrent=self.concurrent,
        )
        await subscribe.configure()

    def run(self, chaos_mode: bool = False):
        task = async_echo_job
        if chaos_mode:
            task = async_chaos_job
        self.loop.run_until_complete(self.init(task))
        self.loop.run_forever()
