from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models.movies import StarModel
from movies.schemas.stars import StarCreateSchema


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

    async def get_star(self, star_id: int):
        query = select(StarModel).where(StarModel.id == star_id)
        result = await self.db.execute(query)
        star = result.scalar_one_or_none()
        return star

    async def add_star(self, star: StarCreateSchema):
        self.db.add(star)
        await self.db.commit()
        await self.db.refresh(star)

    async def update_star(self, star_id: int, new_star: StarCreateSchema):
        star = await self.db.get(StarModel, star_id)

        if not star:
            raise HTTPException(
                status_code=404, detail="Star with the given ID was not found."
            )

        update_data = new_star.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(star, key, value)

        await self.db.commit()
        await self.db.refresh(star)

    async def delete_star(self, star_id: int):
        star = await self.db.get(StarModel, star_id)

        if not star:
            raise HTTPException(
                status_code=404,
                detail="Star with the given ID was not found.",
            )

        await self.db.delete(star)
        await self.db.commit()
