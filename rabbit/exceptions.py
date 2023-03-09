class AttributeNotInitialized(Exception):
    pass


class OperationError(Exception):
    pass


class ExchangeNotFound(Exception):
    def __init__(
        self, exchange_name: str, message: str = "Exchange '{name}' not found"
    ):
        super().__init__(message.format(name=exchange_name))


class ClientNotConnectedError(Exception):
    def __init__(self, message="AioRabbitClient was not connected with RabbitMQ"):
        super().__init__(message)
