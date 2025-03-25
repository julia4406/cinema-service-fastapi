from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.movies import StarModel
from src.movies.repository.movies import MoviesRepository
from src.movies.schemas.movies import (
    MovieListResponseSchema,
    MovieListItemSchema,
    MovieDetailSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
)

class MoviesService:
    def __init__(self, db: AsyncSession):
        self.repository = MoviesRepository(db)

    async def get_movies(
            self,
            page: int = 1,
            per_page: int = 10
    ):
        total_items, movies = await self.repository.get_movies_paginated(page=page, per_page=per_page)

        total_pages = (total_items + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page

        if not movies:
            raise HTTPException(status_code=404, detail="No movies found.")

        return MovieListResponseSchema(
            movies=[
                MovieListItemSchema.model_validate(movie)
                for movie in movies
            ],
            prev_page=(
                f"/?page={page - 1}&per_page={per_page}"
                if page > 1 else None
            ),
            next_page=(
                f"/?page={page + 1}&per_page={per_page}"
                if page < total_pages else None
            ),
            total_pages=total_pages,
            total_items=total_items,
        )

