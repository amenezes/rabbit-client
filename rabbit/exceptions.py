class AttributeNotInitialized(Exception):
    pass


class OperationError(Exception):
    pass


class ExchangeNotFound(Exception):
    pass


class ClientNotConnectedError(Exception):
    def __init__(self, message="AioRabbitClient was not connected with RabbitMQ"):
        super().__init__(message)
