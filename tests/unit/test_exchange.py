import pytest


@pytest.mark.parametrize("attribute", ["name", "exchange_type", "topic", "durable"])
def test_attributes(exchange, attribute):
    assert hasattr(exchange, attribute)
