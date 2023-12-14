class AttributeNotInitialized(Exception):
    def __init__(self, message: str = "Attribute not initialized") -> None:
        super().__init__(message)


class OperationError(Exception):
    def __init__(self, message: str = "OperationError") -> None:
        super().__init__(message)


class ExchangeNotFound(Exception):
    def __init__(self, exchange_name: str) -> None:
        super().__init__(f"Exchange '{exchange_name}' not found")


class ClientNotConnectedError(Exception):
    def __init__(
        self, message: str = "AioRabbitClient was not connected with RabbitMQ"
    ) -> None:
        super().__init__(message)
