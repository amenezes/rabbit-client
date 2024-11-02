class AttributeNotInitialized(Exception):
    def __init__(self) -> None:
        super().__init__("Attribute not initialized")


class OperationError(Exception):
    def __init__(self) -> None:
        super().__init__("OperationError")


class ExchangeNotFound(Exception):
    def __init__(self, exchange_name: str) -> None:
        super().__init__(f"Exchange '{exchange_name}' not found")


class ClientNotConnectedError(Exception):
    def __init__(self) -> None:
        super().__init__("AioRabbitClient was not connected with RabbitMQ")
