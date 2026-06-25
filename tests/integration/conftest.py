import socket

import pytest


def _rabbitmq_reachable() -> bool:
    try:
        sock = socket.create_connection(("localhost", 5672), timeout=2)
        sock.close()
        return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def amqp_url():
    if not _rabbitmq_reachable():
        pytest.skip("RabbitMQ broker not available at localhost:5672")
    return "amqp://guest:guest@localhost:5672/%2F"
