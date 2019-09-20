import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import attr


@attr.s(slots=True)
class Task:

    app = attr.ib(default=asyncio.get_event_loop())
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

    async def execute(self, data, **kwargs):
        if not callable(self.job):
            raise TypeError('Job must be callable.')

        task = [
            self.app.run_in_executor(
                self.process_executor,
                partial(
                    self.job,
                    data,
                    **kwargs
                )
            )
        ]
        completed, *_ = await asyncio.wait(task)
        results = [t.result() for t in completed]
        return results

    @staticmethod
    def echo_job(*args, **kwargs):
        return dict(
            positional_arguments=args,
            keyword_arguments=kwargs
        )
