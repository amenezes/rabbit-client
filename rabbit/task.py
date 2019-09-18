import attr

@attr.s
class Task:

    data = attr.ib(
        type=bytes,
        validator=attr.validators.instance_of(bytes)
    )

    async def execute(self):
        pass