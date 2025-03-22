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
