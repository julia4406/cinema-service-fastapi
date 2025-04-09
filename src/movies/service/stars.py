from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from src.config.logging_settings import logger
from src.database.exceptions.stars import StarCreateError, StarNotFoundError, StarUpdateError
from src.database.models.movies import StarModel
from src.movies.repository.stars import StarsRepository, get_stars_repository
from src.movies.schemas.stars import StarCreateSchema, StarSchema


class StarsService:
    def __init__(self, repository: StarsRepository):
        self.repository = repository
        logger.info("StarsService initialized")

    async def get_stars(self, page: int = 1, per_page: int = 10):
        logger.info(f"Fetching stars with page={page}, per_page={per_page}")
        offset = (page - 1) * per_page
        stars = await self.repository.get_stars(limit=per_page, offset=offset)

        total_items = len(stars) or 0

        if not stars and total_items == 0:
            logger.warning("No stars found")
            raise StarNotFoundError("No stars found.")

        total_pages = (total_items + per_page - 1) // per_page

        base_url = "/theater/movies/"
        prev_page_url = (
            f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
        )
        next_page_url = (
            f"{base_url}?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        )

        logger.info(f"Stars fetched successfully, total pages: {total_pages}, total items: {total_items}")
        response_data = {
            "stars": stars,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items,
        }
        return response_data

    async def get_one_star(self, star_id: int):
        logger.info(f"Fetching star with id={star_id}")
        star = await self.repository.get_star(star_id)
        if not star:
            logger.warning(f"Star with id={star_id} not found")
            raise StarNotFoundError("No star found.")

        logger.info(f"Star found: {star.name}")
        return star

    async def create_star(self, star: StarCreateSchema):
        logger.info(f"Creating star with name={star.name}")
        new_star = StarModel(
            name=star.name,
        )
        existing_star = await self.repository.add_star(new_star)

        if existing_star is False:
            logger.warning(f"A star with the name '{star.name}' already exists")
            raise StarCreateError(
                f"A star with the name '{star.name}' already exists."
            )
        try:
            logger.info(f"Star '{star.name}' created successfully")
            return StarSchema.model_validate(existing_star)

        except IntegrityError:
            logger.error(
                f"Error occurred while creating star with name={star.name}")
            raise StarCreateError("Invalid input data.")

    async def update_star(self, star_id: int, star: StarCreateSchema):
        logger.info(f"Updating star with id={star_id}")
        result = await self.repository.update_star(star_id, star)
        if result:
            logger.info(f"Star with id={star_id} updated successfully")
            return {"detail": "Star updated successfully."}
        else:
            logger.warning(f"Star with id={star_id} not found")
            raise StarUpdateError(
                "Star with the given ID was not found."
            )

    async def delete_star(self, star_id: int):
        logger.info(f"Deleting star with id={star_id}")
        result = await self.repository.delete_star(star_id)

        if result:
            logger.info(f"Star with id={star_id} deleted successfully")
            return
        else:
            logger.warning(f"Star with id={star_id} not found")
            raise StarNotFoundError(
                "Star with the given ID was not found."
            )


def get_stars_service(
    repository: StarsRepository = Depends(get_stars_repository)
) -> StarsService:
    return StarsService(repository)
