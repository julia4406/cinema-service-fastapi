from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models.movies import GenreModel
from movies.schemas.genres import GenreCreateSchema


class GenresRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_genres(self, limit: int = 10, offset: int = 0):
        count_query = select(func.count(GenreModel.id))
        result = await self.db.execute(count_query)
        total_items = result.scalar() or 0

        if total_items == 0:
            raise HTTPException(status_code=404, detail="No genres found.")

        genres = await self.db.execute(select(GenreModel).offset(offset).limit(limit))
        return genres.scalars().all(), total_items

    async def get_genre(self, genre_id: int):
        query = select(GenreModel).where(GenreModel.id == genre_id)
        result = await self.db.execute(query)
        genre = result.scalar_one_or_none()
        return genre

    async def add_genre(self, genre: GenreModel):
        self.db.add(genre)
        await self.db.commit()
        await self.db.refresh(genre)
        return genre

    async def update_genre(self, genre_id: int, new_genre: GenreCreateSchema):
        genre = await self.db.get(GenreModel, genre_id)

        if not genre:
            raise HTTPException(
                status_code=404, detail="Genre with the given ID was not found."
            )

        update_data = new_genre.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(genre, key, value)

        await self.db.commit()
        await self.db.refresh(genre)

    async def delete_genre(self, genre_id: int):
        genre = await self.db.get(GenreModel, genre_id)

        if not genre:
            raise HTTPException(
                status_code=404,
                detail="Genre with the given ID was not found.",
            )

        await self.db.delete(genre)
        await self.db.commit()
