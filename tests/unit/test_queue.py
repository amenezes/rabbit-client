import attr


def test_attributes(queue):
    values = ["queue", True, {}]
    for value in values:
        assert value in attr.asdict(queue).values()
