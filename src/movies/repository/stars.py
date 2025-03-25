from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.movies import StarModel
from movies.schemas.stars import StarCreateSchema


class StarsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_star_by_name(self, name: str):
        existing_stmt = select(StarModel).where(
            (StarModel.name == name)
        )

        existing_result = await self.db.execute(existing_stmt)
        existing_genre = existing_result.scalars().first()
        return True if existing_genre else False

    async def get_stars(self, limit: int = 10, offset: int = 0):
        stars = await self.db.execute(select(StarModel).offset(offset).limit(limit))
        return stars.scalars().all()

    async def get_star(self, star_id: int):
        query = select(StarModel).where(StarModel.id == star_id)
        result = await self.db.execute(query)
        star = result.scalar_one_or_none()
        return star

    async def add_star(self, star: StarModel):
        if await self.is_star_by_name(star.name):
            return False

        self.db.add(star)
        await self.db.commit()
        await self.db.refresh(star)
        return star

    async def update_star(self, star_id: int, new_star: StarCreateSchema):
        star = await self.db.get(StarModel, star_id)

        if star:
            update_data = new_star.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(star, key, value)

            await self.db.commit()
            await self.db.refresh(star)
            return star

        return None

    async def delete_star(self, star_id: int):
        star = await self.db.get(StarModel, star_id)

        if star:
            await self.db.delete(star)
            await self.db.commit()
            return True

        return False
