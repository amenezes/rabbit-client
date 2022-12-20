class AttributeNotInitialized(Exception):
    def __init__(self, message: str = "Connection not initialized."):
        super().__init__(message)


class OperationError(Exception):
    def __init__(self, message: str = "Ensure that instance was connected "):
        super().__init__(message)


class ExchangeNotFound(Exception):
    def __init__(
        self, exchange_name: str, message: str = "Exchange '{exchange_name}' not found"
    ):
        super().__init__(message.format(exchange_name=exchange_name))
