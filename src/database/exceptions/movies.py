class MoviesBaseError(Exception):
    pass


class MovieNotFoundError(MoviesBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MovieAlreadyExistsError(MoviesBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MovieCreateError(MoviesBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MovieUpdateError(MoviesBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MovieDeleteError(MoviesBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
