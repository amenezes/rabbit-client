import pytest


@pytest.mark.parametrize("attribute", ["name", "durable", "arguments"])
def test_attributes(queue, attribute):
    assert hasattr(queue, attribute)
