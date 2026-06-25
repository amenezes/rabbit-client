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
    ) -> None:
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.exchange_topic = exchange_topic
        self.queue_name = queue_name
        self.concurrent = concurrent

    def run(self, chaos_mode: bool = False, verbose: bool = True) -> None:
        task = async_echo_job if not chaos_mode else async_chaos_job
        try:
            asyncio.run(self._run(task, verbose))
        except KeyboardInterrupt:
            pass

    async def _run(self, task, verbose: bool = False) -> None:
        logger.info(f"Using '{task.__doc__}'")
        client = AioRabbitClient()
        await client.connect(
            host=self.host,
            port=self.port,
            login=self.login,
            password=self.password,
        )
        channel = await client.channel()

        subscribe = Subscribe(
            task=task,
            exchange=Exchange(
                self.exchange_name, self.exchange_type, self.exchange_topic
            ),
            queue=Queue(name=self.queue_name),
            concurrent=self.concurrent,
        )
        await subscribe.configure(channel)

        if verbose:
            logger.info(
                "Consumer ready — waiting for messages on " f"queue '{self.queue_name}'"
            )

        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            pass
        finally:
            await client.close()
