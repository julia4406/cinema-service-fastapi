from typing import Type, Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.logging_settings import logger
from src.database.models.movies import GenreModel
from src.database.session_postgresql import get_postgresql_db as get_db
from src.movies.schemas.genres import GenreCreateSchema


class GenresRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def is_genre_by_name(self, name: str) -> bool:
        logger.info(f"Checking if genre with name '{name}' exists")
        existing_stmt = select(GenreModel).where((GenreModel.name == name))

        existing_result = await self.db.execute(existing_stmt)
        existing_genre = existing_result.scalars().first()
        if existing_genre:
            logger.info(f"Genre with name '{name}' exists")
        else:
            logger.info(f"Genre with name '{name}' does not exist")
        return True if existing_genre else False

    async def get_genres(
            self, limit: int = 10, offset: int = 0
    ) -> Sequence[GenreModel]:
        logger.info(f"Fetching genres with limit={limit}, offset={offset}")
        genres = await self.db.execute(select(GenreModel).offset(offset).limit(limit))
        genre_list = genres.scalars().all()
        logger.info(f"Fetched {len(genre_list)} genres")
        return genre_list

    async def get_genre(self, genre_id: int) -> GenreModel:
        logger.info(f"Fetching genre with id={genre_id}")
        query = select(GenreModel).where(GenreModel.id == genre_id)
        result = await self.db.execute(query)
        genre = result.scalar_one_or_none()
        if genre:
            logger.info(f"Found genre with id={genre_id}")
        else:
            logger.warning(f"Genre with id={genre_id} not found")
        return genre

    async def add_genre(self, genre: GenreModel) -> bool | GenreModel:
        logger.info(f"Adding genre with name '{genre.name}'")
        if await self.is_genre_by_name(genre.name):
            logger.warning(f"Genre with name '{genre.name}' already exists")
            return False

        self.db.add(genre)
        await self.db.commit()
        await self.db.refresh(genre)
        logger.info(f"Added genre with id={genre.id} and name '{genre.name}'")
        return genre

    async def update_genre(
            self, genre_id: int, new_genre: GenreCreateSchema
    ) -> Type[GenreModel] | None:
        logger.info(f"Updating genre with id={genre_id}")
        genre = await self.db.get(GenreModel, genre_id)

        if genre:
            update_data = new_genre.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(genre, key, value)

            await self.db.commit()
            await self.db.refresh(genre)
            logger.info(f"Updated genre with id={genre_id}")
            return genre

        logger.warning(f"Genre with id={genre_id} not found for update")
        return None

    async def delete_genre(self, genre_id: int) -> bool:
        logger.info(f"Deleting genre with id={genre_id}")
        genre = await self.db.get(GenreModel, genre_id)

        if genre:
            await self.db.delete(genre)
            await self.db.commit()
            logger.info(f"Deleted genre with id={genre_id}")
            return True

        logger.warning(f"Genre with id={genre_id} not found for deletion")
        return False


def get_genres_repository(db: AsyncSession = Depends(get_db)) -> GenresRepository:
    return GenresRepository(db)
