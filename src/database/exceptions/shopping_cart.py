class CartBaseError(Exception):
    pass


class CreateCartError(CartBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CreatePurchaseError(CartBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CartItemError(CartBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
