from attrs import field, frozen, validators


@frozen
class Queue:
    name: str = field(validator=validators.instance_of(str))
    durable: bool = field(default=True, validator=validators.instance_of(bool))
    arguments: dict = field(factory=dict, validator=validators.instance_of(dict))
