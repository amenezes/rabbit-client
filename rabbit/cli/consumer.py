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
        host: str,
        port: int,
        login: str,
        password: str,
        exchange_name: str,
        exchange_type: str,
        exchange_topic: str,
        queue_name: str,
        concurrent: int,
    ):
        self.subscribe_client = AioRabbitClient()

        self._loop = asyncio.get_event_loop()
        self._loop.create_task(
            self.subscribe_client.persistent_connect(
                host=host, port=port, login=login, password=password
            ),
            name="rabbit-client-cli-connection",
        )

        self.exchange_type = exchange_type
        self.exchange_topic = exchange_topic
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.concurrent = concurrent

    def run(self, chaos_mode: bool = False, verbose: bool = True):
        task = async_echo_job
        if chaos_mode:
            task = async_chaos_job

        self._loop.run_until_complete(self.init(task, verbose))
        self._loop.run_forever()

    async def init(self, task, verbose: bool = False):
        logger.info(f"Using '{task.__doc__}'")
        subscribe = Subscribe(
            task=task,
            exchange=Exchange(
                self.exchange_name, self.exchange_type, self.exchange_topic
            ),
            queue=Queue(name=self.queue_name),
            concurrent=self.concurrent,
        )
        await self.subscribe_client.register(subscribe)
        if verbose:
            while True:
                await asyncio.sleep(10)
                logger.debug(repr(self.subscribe_client))
