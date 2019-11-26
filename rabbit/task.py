import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Task:

    _app = attr.ib(default=asyncio.get_event_loop())
    job = attr.ib(
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.is_callable()
        )
    )
    process = attr.ib(
        type=ProcessPoolExecutor,
        default=ProcessPoolExecutor(max_workers=1),
        validator=attr.validators.instance_of(ProcessPoolExecutor)
    )

    async def process_executor(self, *args, **kwargs):
        logging.debug('Starting ProcessPoolExecutor...')
        logging.debug(f'args received: {args}')
        logging.debug(f'kwargs receveid: {kwargs}')

        attr.validate(self)
        task = [
            self._app.run_in_executor(
                self.process,
                partial(
                    self.job,
                    *args,
                    **kwargs
                )
            )
        ]
        completed, *_ = await asyncio.wait(task)
        return (t.result() for t in completed)

    async def std_executor(self, *args, **kwargs):
        logging.debug('Starting StandardExecutor...')
        logging.debug(f'args received: {args}')
        logging.debug(f'kwargs receveid: {kwargs}')

        attr.validate(self)
        if asyncio.iscoroutinefunction(self.job):
            result = await self.job(*args, **kwargs)
            return [result]
        result = self.job(*args, **kwargs)
        return [result]
