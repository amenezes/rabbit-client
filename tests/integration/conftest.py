import pytest


@pytest.fixture(scope="session")
def amqp_url():
    return "amqp://guest:guest@localhost:5672/%2F"
