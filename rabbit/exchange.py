import logging

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Exchange:

    name = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    exchange_type = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    topic = attr.ib(
        type=str,
        default='',
        validator=attr.validators.instance_of(str)
    )
