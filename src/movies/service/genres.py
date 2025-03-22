from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.movies import GenreModel
from movies.repository.genres import GenresRepository
from movies.schemas.genres import GenreSchema, GenreCreateSchema


class GenresService:
    def __init__(self, db: AsyncSession):
        self.repository = GenresRepository(db)
        self.db = db

    async def get_genres(
            self,
            page: int = 1,
            per_page: int = 10
    ):
        offset = (page - 1) * per_page
        genres, total_items = await self.repository.get_genres(limit=per_page, offset=offset)

        if not genres and total_items == 0:
            raise HTTPException(status_code=404, detail="No genres found.")

        total_pages = (total_items + per_page - 1) // per_page

        base_url = "/theater/genres/"
        prev_page_url = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
        next_page_url = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

        response_data = {
            "genres": genres,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items
        }
        return response_data
