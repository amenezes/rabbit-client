from datetime import datetime
from typing import Optional

import attr


@attr.s(slots=True)
class Event:

    body = attr.ib(
        type=bytes,
        validator=attr.validators.instance_of(bytes)
    )
    identity = attr.ib(
        type=Optional[int],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(int)
        )
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
        default=False,
        validator=attr.validators.instance_of(bool)
    )
