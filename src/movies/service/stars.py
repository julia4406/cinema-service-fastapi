from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.movies import StarModel
from src.movies.repository.stars import StarsRepository
from src.movies.schemas.stars import StarSchema, StarCreateSchema


class StarsService:
    def __init__(self, db: AsyncSession):
        self.repository = StarsRepository(db)

    async def get_stars(self, page: int = 1, per_page: int = 10):
        offset = (page - 1) * per_page
        stars = await self.repository.get_stars(limit=per_page, offset=offset)

        total_items = len(stars) or 0

        if not stars and total_items == 0:
            raise HTTPException(status_code=404, detail="No stars found.")

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

        response_data = {
            "stars": stars,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items,
        }
        return response_data

    async def get_one_star(self, star_id: int):
        star = await self.repository.get_star(star_id)
        if not star:
            raise HTTPException(status_code=404, detail="No star found.")

        return star

    async def create_star(self, star: StarCreateSchema):
        new_star = StarModel(
            name=star.name,
        )
        existing_star = await self.repository.add_star(new_star)

        if existing_star is False:
            raise HTTPException(
                status_code=409,
                detail=(f"A star with the name '{star.name}' already exists."),
            )
        try:
            return StarSchema.model_validate(existing_star)

        except IntegrityError:
            raise HTTPException(status_code=400, detail="Invalid input data.")

    async def update_star(self, star_id: int, star: StarCreateSchema):
        result = await self.repository.update_star(star_id, star)
        if result:
            return {"detail": "Star updated successfully."}
        else:
            raise HTTPException(
                status_code=404, detail="Star with the given ID was not found."
            )

    async def delete_star(self, star_id: int):
        result = await self.repository.delete_star(star_id)

        if result:
            return
        else:
            raise HTTPException(
                status_code=404,
                detail="Star with the given ID was not found.",
            )
