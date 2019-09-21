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
    process_executor = attr.ib(
        type=ProcessPoolExecutor,
        default=ProcessPoolExecutor(max_workers=1),
        validator=attr.validators.instance_of(ProcessPoolExecutor)
    )

    async def execute(self, *args, **kwargs):
        if not callable(self.job):
            raise TypeError('Job must be callable.')

        logging.debug('Starting ProcessPoolExecutor...')
        logging.debug(f'args received: {args}')
        logging.debug(f'kwargs receveid: {kwargs}')
        task = [
            self._app.run_in_executor(
                self.process_executor,
                partial(
                    self.job,
                    *args,
                    **kwargs
                )
            )
        ]
        completed, *_ = await asyncio.wait(task)
        results = [t.result() for t in completed]
        return results
