class GenreBaseError(Exception):
    pass


class GenreNotFoundError(GenreBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CreateGenreError(GenreBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UpdateGenreError(GenreBaseError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
