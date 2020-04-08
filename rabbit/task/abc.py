import abc
from typing import Callable

import attr

from rabbit import echo_job


@attr.s
class Task(abc.ABC):
    job = attr.ib(
        type=Callable, default=echo_job, validator=attr.validators.is_callable()
    )

    async def execute(self, *args, **kwargs):
        raise NotImplementedError
