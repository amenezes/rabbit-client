import asyncio
from typing import Dict, Generator, List

from attrs import field, mutable, validators


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

    def add(self, name: str, task: asyncio.Task) -> None:
        if name not in self._tasks.keys():
            self._tasks.update({name: task})

    def discard(self, task: asyncio.Task) -> None:
        try:
            del self._tasks[task.get_name()]
        except KeyError:
            pass

    def tasks_by_name(self) -> List[str]:
        return [task_name for task_name in self._tasks.keys()]

    def __iter__(self) -> Generator[asyncio.Task, None, None]:
        for _, task in self._tasks.items():
            yield task

    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        return f"BackgroundTasks(tasks={len(self)})"
