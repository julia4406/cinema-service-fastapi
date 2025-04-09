from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from src.config.logging_settings import logger
from src.database.exceptions.genres import CreateGenreError, GenreNotFoundError, UpdateGenreError
from src.database.models.movies import GenreModel
from src.movies.repository.genres import GenresRepository, get_genres_repository
from src.movies.schemas.genres import GenreCreateSchema, GenreSchema


class GenresService:
    def __init__(self, repository: GenresRepository) -> None:
        self.repository = repository
        logger.info("GenresService initialized")

    async def get_genres(self, page: int = 1, per_page: int = 10) -> dict:
        offset = (page - 1) * per_page
        logger.info(f"Fetching genres with page={page}, per_page={per_page}")
        genres = await self.repository.get_genres(limit=per_page, offset=offset)

        total_items = len(genres) or 0

        if not genres and total_items == 0:
            logger.warning("No genres found")
            raise GenreNotFoundError("No genres found.")

        total_pages = (total_items + per_page - 1) // per_page
        logger.info(f"Total pages: {total_pages}, Total items: {total_items}")

        base_url = "/theater/genres/"
        prev_page_url = (
            f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
        )
        next_page_url = (
            f"{base_url}?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        )

        response_data = {
            "genres": genres,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items,
        }
        logger.info("Genres fetched successfully")
        return response_data

    async def get_one_genre(self, genre_id: int) -> GenreModel:
        logger.info(f"Fetching genre with id={genre_id}")
        genre = await self.repository.get_genre(genre_id)
        if not genre:
            logger.warning(f"Genre with id={genre_id} not found")
            raise GenreNotFoundError("No genre found.")
        logger.info(f"Genre found: {genre.name}")
        return genre

    async def create_genre(self, genre: GenreCreateSchema) -> GenreSchema:
        logger.info(f"Creating genre: {genre.name}")
        new_genre = GenreModel(
            name=genre.name,
        )

        created_genre = await self.repository.add_genre(new_genre)

        if created_genre is False:
            logger.warning(f"Genre with name '{genre.name}' already exists")
            raise CreateGenreError(f"A genre with the name '{genre.name}' already exists.")
        try:
            logger.info(f"Genre created successfully: {genre.name}")
            return GenreSchema.model_validate(created_genre)

        except IntegrityError:
            logger.error("IntegrityError occurred during genre creation")
            raise CreateGenreError("Invalid input data.")

    async def update_genre(self, genre_id: int, genre: GenreCreateSchema) -> dict:
        logger.info(f"Updating genre with id={genre_id}")
        result = await self.repository.update_genre(genre_id, genre)
        if result:
            logger.info(f"Genre with id={genre_id} updated successfully")
            return {"detail": "Genre updated successfully."}
        else:
            logger.warning(f"Genre with id={genre_id} not found for update")
            raise UpdateGenreError(
                "Genre with the given ID was not found."
            )

    async def delete_genre(self, genre_id: int) -> None:
        logger.info(f"Deleting genre with id={genre_id}")
        result = await self.repository.delete_genre(genre_id)

        if result:
            logger.info(f"Genre with id={genre_id} deleted successfully")
            return
        else:
            logger.warning(f"Genre with id={genre_id} not found for deletion")
            raise GenreNotFoundError(
                "Genre with the given ID was not found.",
            )


def get_genres_service(
    repository: GenresRepository = Depends(get_genres_repository)
) -> GenresService:
    return GenresService(repository)
