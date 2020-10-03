import attr


@attr.s(frozen=True)
class Exchange:
    name = attr.ib(type=str, validator=attr.validators.instance_of(str))
    exchange_type = attr.ib(type=str, validator=attr.validators.instance_of(str))
    topic = attr.ib(type=str, default="#", validator=attr.validators.instance_of(str))
    durable = attr.ib(
        type=bool, default=True, validator=attr.validators.instance_of(bool)
    )
