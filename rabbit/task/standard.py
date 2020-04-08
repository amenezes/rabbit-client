import asyncio
import logging

import attr

from rabbit.task import Task

logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s
class StandardTask(Task):
    async def execute(self, *args, **kwargs):
        logging.debug("Starting StandardExecutor...")
        logging.debug(f"args received: {args}")
        logging.debug(f"kwargs receveid: {kwargs}")

        attr.validate(self)
        if asyncio.iscoroutinefunction(self.job):
            result = await self.job(*args, **kwargs)
            return [result]
        return [self.job(*args, **kwargs)]
