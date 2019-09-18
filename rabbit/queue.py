import logging

import attr


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Queues:

    name = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    durable = attr.ib(
        type=bool,
        default=True,
        validator=attr.validators.instance_of(bool)
    )
    suffix = attr.ib(
        type=str,
        default='',
        validator=attr.validators.instance_of(str)
    )
    arguments = attr.ib(
        type=dict,
        default={},
        validator=attr.validators.instance_of(dict)
    )
