from rabbit.exceptions import ClientNotConnectedError, ExchangeNotFound


def test_exchange_not_found_message():
    assert (
        str(ExchangeNotFound("test-exchange")) == "Exchange 'test-exchange' not found"
    )


def test_client_not_connected_error():
    assert (
        str(ClientNotConnectedError())
        == "AioRabbitClient was not connected with RabbitMQ"
    )
