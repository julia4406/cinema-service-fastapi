from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from movies.repository.stars import StarsRepository


class StarsService:
    def __init__(self, db: AsyncSession):
        self.repository = StarsRepository(db)
        self.db = db

    async def get_stars(
            self,
            page: int = 1,
            per_page: int = 10
    ):
        offset = (page - 1) * per_page
        stars, total_items = await self.repository.get_stars(limit=per_page, offset=offset)

        if not stars and total_items == 0:
            raise HTTPException(status_code=404, detail="No stars found.")

        total_pages = (total_items + per_page - 1) // per_page

        base_url = "/theater/movies/"
        prev_page_url = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
        next_page_url = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

        response_data = {
            "stars": stars,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items
        }
        return response_data

    async def get_one_star(self, star_id: int):
        star = await self.repository.get_star(star_id)
        if not star:
            raise HTTPException(status_code=404, detail="No star found.")

        return star
