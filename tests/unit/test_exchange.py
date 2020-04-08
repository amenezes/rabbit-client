import attr


def test_attributes(exchange):
    values = ["exchange", "topic", "#"]
    for value in values:
        assert value in attr.asdict(exchange).values()
