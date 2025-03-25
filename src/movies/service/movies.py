from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from src.movies.repository.movies import MoviesRepository
from src.movies.schemas.movies import (
    MovieListResponseSchema,
    MovieListItemSchema,
    MovieDetailSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    DetailMessageSchema, MovieLikeResponseSchema, MovieFavoriteResponseSchema, MovieSortEnum,
)


class MoviesService:
    def __init__(self, db: AsyncSession):
        self.repository = MoviesRepository(db)

    async def get_movies(
            self,
            filters: dict[str, str],
            sort_by: Optional[MovieSortEnum] = None,
            page: int = 1,
            per_page: int = 10,
    ):
        filtered_movies = await self.repository.filter_movies(filters, sort_by)

        total_items = len(filtered_movies)
        total_pages = (total_items + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page

        paginated_movies = filtered_movies[start:end]

        if not paginated_movies:
            raise HTTPException(status_code=404, detail="No movies found.")

        return MovieListResponseSchema(
            movies=[
                MovieListItemSchema.model_validate(movie)
                for movie in paginated_movies
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

    async def get_movie_by_id(self, movie_id):
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        return MovieDetailSchema.model_validate(movie)

    async def create_movie(self, movie_data: MovieCreateSchema):
        existing_movie = await self.repository.get_movie_by_name(movie_data)

        if existing_movie:
            raise HTTPException(
                status_code=409,
                detail="Movie already exists.",
            )

        try:
            movie = await self.repository.create_movie_post(movie_data)
            return MovieDetailSchema.model_validate(movie)
        except HTTPException:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Invalid input data.")

    async def update_movie(self, movie_id: int, movie_data: MovieUpdateSchema):
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        for field, value in movie_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(movie, field, value)

        try:
            await self.repository.commit_instance(movie)
        except HTTPException:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Invalid input data.")
        else:
            return DetailMessageSchema(detail="Movie updated successfully.")

    async def delete_movie(self, movie_id: int):
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        result = await self.repository.delete_instance(movie)
        if result:
            raise HTTPException(status_code=404, detail="Movie was purchased.")
        return

    async def like_or_dislike_movie(
            self,
            movie_id: int,
            user: UserModel
    ) -> MovieLikeResponseSchema:
        movie = await self.repository.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(
                status_code=404,
                detail="Movie with the given ID was not found."
            )

        movie_like = await self.repository.toggle_movie_like(movie, user.id)

        return MovieLikeResponseSchema(
            is_liked=movie_like.is_liked,
            created_at=movie_like.created_at,
            user=user.id,
            movie=movie.id,
        )

    async def favorite_or_unfavorite(
            self,
            movie_id: int,
            user: UserModel
    ) -> MovieFavoriteResponseSchema:
        movie = await self.repository.get_movie_by_id(movie_id)
        if not movie:
            raise HTTPException(
                status_code=404,
                detail="Movie with the given ID was not found."
            )

        movie_favorite = await self.repository.toggle_movie_favorite(movie, user.id)

        return MovieFavoriteResponseSchema(
            is_favorite=movie_favorite.is_favorite,
            added_at=movie_favorite.added_at,
            user=user.id,
            movie=movie.id,
        )
