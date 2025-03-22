from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models.movies import StarModel


class StarsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stars(self, limit: int = 10, offset: int = 0):
        count_query = select(func.count(StarModel.id))
        result = await self.db.execute(count_query)
        total_items = result.scalar() or 0

        if total_items == 0:
            raise HTTPException(status_code=404, detail="No stars found.")

        stars = await self.db.execute(select(StarModel).offset(offset).limit(limit))
        return stars.scalars().all(), total_items
