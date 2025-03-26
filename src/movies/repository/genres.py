from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.movies import GenreModel
from src.movies.schemas.genres import GenreCreateSchema


class GenresRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_genre_by_name(self, name: str):
        existing_stmt = select(GenreModel).where(
            (GenreModel.name == name)
        )

        existing_result = await self.db.execute(existing_stmt)
        existing_genre = existing_result.scalars().first()
        return True if existing_genre else False

    async def get_genres(self, limit: int = 10, offset: int = 0):
        genres = await self.db.execute(select(GenreModel).offset(offset).limit(limit))
        return genres.scalars().all()

    async def get_genre(self, genre_id: int):
        query = select(GenreModel).where(GenreModel.id == genre_id)
        result = await self.db.execute(query)
        genre = result.scalar_one_or_none()
        return genre

    async def add_genre(self, genre: GenreModel):
        if await self.is_genre_by_name(genre.name):
            return False

        self.db.add(genre)
        await self.db.commit()
        await self.db.refresh(genre)
        return genre

    async def update_genre(self, genre_id: int, new_genre: GenreCreateSchema):
        genre = await self.db.get(GenreModel, genre_id)

        if genre:
            update_data = new_genre.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(genre, key, value)

            await self.db.commit()
            await self.db.refresh(genre)
            return genre

        return None

    async def delete_genre(self, genre_id: int):
        genre = await self.db.get(GenreModel, genre_id)

        if genre:
            await self.db.delete(genre)
            await self.db.commit()
            return True

        return False
