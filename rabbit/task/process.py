import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import attr

from rabbit import loop
from rabbit.task import Task

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s
class ProcessTask(Task):
    process = attr.ib(
        type=ProcessPoolExecutor,
        default=ProcessPoolExecutor(max_workers=1),
        validator=attr.validators.instance_of(ProcessPoolExecutor),
    )
    _loop = attr.ib(default=None)

    async def execute(self, *args, **kwargs):
        logging.debug("Starting ProcessPoolExecutor...")
        logging.debug(f"args received: {args}")
        logging.debug(f"kwargs receveid: {kwargs}")

        attr.validate(self)
        task = [
            self.loop.run_in_executor(self.process, partial(self.job, *args, **kwargs))
        ]
        completed, *_ = await asyncio.wait(task)
        return (t.result() for t in completed)

    @property
    def loop(self):
        if not self._loop:
            return loop()
        return self._loop
