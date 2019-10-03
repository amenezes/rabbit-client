from datetime import datetime

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
    status = attr.ib(
        type=bool,
        default=False
    )
    created = attr.ib(
        type=datetime,
        default=datetime.utcnow()
    )
