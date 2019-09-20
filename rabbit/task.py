import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import attr


@attr.s
class Task:

    app = attr.ib(default=asyncio.get_event_loop())
    process_executor = attr.ib(
        type=ProcessPoolExecutor,
        default=ProcessPoolExecutor(max_workers=1),
        validator=attr.validators.instance_of(ProcessPoolExecutor)
    )

    async def execute(self, data):
        task = [
            self.app.loop.run_in_executor(
                self.process_executor, partial(
                )
            )
        ]
        completed, *_ = await asyncio.wait(task)
        result = {'status': 'OK', 'data': f'{data}'}
        # results = [t.result() for t in completed]
        # result = await self.format_process_result(peca, process_id, results[0])
        return result
