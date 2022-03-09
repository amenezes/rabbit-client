from attrs import field, frozen, validators


@frozen
class Exchange:
    name: str = field(validator=validators.instance_of(str))
    exchange_type: str = field(validator=validators.instance_of(str))
    topic: str = field(default="#", validator=validators.instance_of(str))
    durable: bool = field(default=True, validator=validators.instance_of(bool))
