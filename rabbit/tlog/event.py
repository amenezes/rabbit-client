from datetime import datetime
from typing import Optional

import attr


@attr.s
class Event:

    identity = attr.ib(
        type=int,
        init=False
    )
    body = attr.ib(
        type=bytes
    )
    created_at = attr.ib(
        type=Optional[datetime],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(datetime)
        )
    )
    created_by = attr.ib(
        type=str,
        default='',
        validator=attr.validators.instance_of(str)
    )
    status = attr.ib(
        type=bool,
        default=False
    )
