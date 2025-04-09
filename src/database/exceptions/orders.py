class OrderBaseError(Exception):
    pass


class CreateOrderError(OrderBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class OrderUpdateError(OrderBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
