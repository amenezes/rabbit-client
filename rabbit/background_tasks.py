import asyncio
from contextlib import suppress
from typing import Dict, Generator, List

from attrs import field, mutable, validators

from rabbit.logger import logger


@mutable
class BackgroundTasks:
    _tasks: Dict[str, asyncio.Task] = field(
        factory=dict,
        validator=[
            validators.instance_of(dict),
            validators.deep_mapping(
                key_validator=validators.instance_of(str),
                value_validator=validators.instance_of(asyncio.Task),
            ),
        ],
    )

    def add(self, name: str, awt, *args, **kwargs) -> None:
        loop = asyncio.get_running_loop()
        logger.debug(f"Trying registering task: '{name}'")

        if name not in self.tasks_by_name():
            logger.debug(f"Registering task: '{name}'")
            task_runner = loop.create_task(awt(*args, **kwargs), name=name)
            task_runner.add_done_callback(self.discard)
            self._tasks.update({name: task_runner})

    def discard(self, task: asyncio.Task) -> None:
        with suppress(KeyError):
            del self._tasks[task.get_name()]

    def tasks_by_name(self) -> List[str]:
        return [task_name for task_name in self._tasks.keys()]

    def __iter__(self) -> Generator[asyncio.Task, None, None]:
        for _, task in self._tasks.items():
            yield task

    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        return (
            f"BackgroundTasks(tasks={len(self)}, tasks_by_name={self.tasks_by_name()})"
        )
