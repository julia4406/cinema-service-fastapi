from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.config.logging_settings import logger
from src.database.models.movies import StarModel
from src.movies.schemas.stars import StarCreateSchema

class StarsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("StarsRepository initialized")

    async def is_star_by_name(self, name: str):
        logger.info(f"Checking if star exists by name: {name}")
        existing_stmt = select(StarModel).where((StarModel.name == name))
        existing_result = await self.db.execute(existing_stmt)
        existing_star = existing_result.scalars().first()
        exists = True if existing_star else False
        logger.info(f"Star exists: {exists}")
        return exists

    async def get_stars(self, limit: int = 10, offset: int = 0):
        logger.info(f"Fetching stars with limit={limit} and offset={offset}")
        stars = await self.db.execute(select(StarModel).offset(offset).limit(limit))
        stars_list = stars.scalars().all()
        logger.info(f"Found {len(stars_list)} stars")
        return stars_list

    async def get_star(self, star_id: int):
        logger.info(f"Fetching star with id={star_id}")
        query = select(StarModel).where(StarModel.id == star_id)
        result = await self.db.execute(query)
        star = result.scalar_one_or_none()
        if star:
            logger.info(f"Star found: {star.name}")
        else:
            logger.warning(f"Star with id={star_id} not found")
        return star

    async def add_star(self, star: StarModel):
        logger.info(f"Adding new star: {star.name}")
        if await self.is_star_by_name(star.name):
            logger.warning(f"Star with name {star.name} already exists")
            return False

        self.db.add(star)
        await self.db.commit()
        await self.db.refresh(star)
        logger.info(f"Star added: {star.name}")
        return star

    async def update_star(self, star_id: int, new_star: StarCreateSchema):
        logger.info(f"Updating star with id={star_id}")
        star = await self.db.get(StarModel, star_id)

        if star:
            update_data = new_star.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(star, key, value)

            await self.db.commit()
            await self.db.refresh(star)
            logger.info(f"Star updated: {star.name}")
            return star

        logger.warning(f"Star with id={star_id} not found for update")
        return None

    async def delete_star(self, star_id: int):
        logger.info(f"Deleting star with id={star_id}")
        star = await self.db.get(StarModel, star_id)

        if star:
            await self.db.delete(star)
            await self.db.commit()
            logger.info(f"Star deleted: {star.name}")
            return True

        logger.warning(f"Star with id={star_id} not found for deletion")
        return False
