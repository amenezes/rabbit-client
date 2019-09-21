import attr


@attr.s(slots=True, frozen=True)
class Queue:

    name = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    durable = attr.ib(
        type=bool,
        default=True,
        validator=attr.validators.instance_of(bool)
    )
    arguments = attr.ib(
        type=dict,
        default={},
        validator=attr.validators.instance_of(dict)
    )
