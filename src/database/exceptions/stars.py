class StarBaseError(Exception):
    pass


class StarNotFoundError(StarBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class StarCreateError(StarBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class StarUpdateError(StarBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
