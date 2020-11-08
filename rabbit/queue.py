import attr


@attr.s(frozen=True)
class Queue:
    name = attr.ib(type=str, validator=attr.validators.instance_of(str))
    durable = attr.ib(
        type=bool, default=True, validator=attr.validators.instance_of(bool)
    )
    arguments = attr.ib(
        type=dict, factory=dict, validator=attr.validators.instance_of(dict)
    )
