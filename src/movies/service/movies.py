from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_settings import logger
from src.database.models import UserModel
from src.movies.repository.movies import MoviesRepository
from src.movies.schemas.movies import (
    MovieListResponseSchema,
    MovieListItemSchema,
    MovieDetailSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    DetailMessageSchema,
    MovieLikeResponseSchema,
    MovieFavoriteResponseSchema,
    MovieSortEnum,
)


class MoviesService:
    def __init__(self, db: AsyncSession):
        self.repository = MoviesRepository(db)
        logger.info("MoviesService initialized")

    async def get_movies(
        self,
        filters: dict[str, str],
        user: UserModel = None,
        sort_by: Optional[MovieSortEnum] = None,
        page: int = 1,
        per_page: int = 10,
    ):
        logger.info(f"Fetching movies with filters={filters}, sort_by={sort_by}, page={page}, per_page={per_page}")
        filtered_movies = await self.repository.filter_movies(filters, sort_by, user)

        total_items = len(filtered_movies)
        total_pages = (total_items + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page

        paginated_movies = filtered_movies[start:end]

        if not paginated_movies:
            logger.warning("No movies found")
            raise HTTPException(status_code=404, detail="No movies found.")

        logger.info(f"Movies fetched successfully, total pages: {total_pages}, total items: {total_items}")
        return MovieListResponseSchema(
            movies=[
                MovieListItemSchema.model_validate(movie) for movie in paginated_movies
            ],
            prev_page=(f"/?page={page - 1}&per_page={per_page}" if page > 1 else None),
            next_page=(
                f"/?page={page + 1}&per_page={per_page}" if page < total_pages else None
            ),
            total_pages=total_pages,
            total_items=total_items,
        )

    async def get_movie_by_id(self, movie_id):
        logger.info(f"Fetching movie with id={movie_id}")
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            logger.warning(f"Movie with id={movie_id} not found")
            raise HTTPException(status_code=404, detail="Movie not found")

        logger.info(f"Movie found: {movie.title}")
        return MovieDetailSchema.model_validate(movie)

    async def create_movie(self, movie_data: MovieCreateSchema):
        logger.info(f"Creating movie: {movie_data.title}")
        existing_movie = await self.repository.get_movie_by_name(movie_data)

        if existing_movie:
            logger.warning(f"Movie '{movie_data.title}' already exists")
            raise HTTPException(
                status_code=409,
                detail="Movie already exists.",
            )

        try:
            movie = await self.repository.create_movie_post(movie_data)
            logger.info(f"Movie '{movie_data.title}' created successfully")
            return MovieDetailSchema.model_validate(movie)
        except HTTPException:
            logger.error("Error occurred while creating movie")
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Invalid input data.")

    async def update_movie(self, movie_id: int, movie_data: MovieUpdateSchema):
        logger.info(f"Updating movie with id={movie_id}")
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            logger.warning(f"Movie with id={movie_id} not found")
            raise HTTPException(status_code=404, detail="Movie not found")

        for field, value in movie_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(movie, field, value)

        try:
            await self.repository.commit_instance(movie)
            logger.info(f"Movie with id={movie_id} updated successfully")
        except HTTPException:
            logger.error(f"Error occurred while updating movie with id={movie_id}")
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Invalid input data.")
        else:
            return DetailMessageSchema(detail="Movie updated successfully.")

    async def delete_movie(self, movie_id: int):
        logger.info(f"Deleting movie with id={movie_id}")
        movie = await self.repository.get_movie_by_id(movie_id)

        if not movie:
            logger.warning(f"Movie with id={movie_id} not found")
            raise HTTPException(status_code=404, detail="Movie not found")

        result = await self.repository.delete_instance(movie)
        if result:
            logger.warning(f"Movie with id={movie_id} was purchased and cannot be deleted")
            raise HTTPException(status_code=404, detail="Movie was purchased.")
        logger.info(f"Movie with id={movie_id} deleted successfully")
        return

    async def like_or_dislike_movie(
        self, movie_id: int, user: UserModel
    ) -> MovieLikeResponseSchema:
        logger.info(f"User {user.id} liking or disliking movie with id={movie_id}")
        movie = await self.repository.get_movie_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie with id={movie_id} not found")
            raise HTTPException(
                status_code=404, detail="Movie with the given ID was not found."
            )

        movie_like = await self.repository.toggle_movie_like(movie, user.id)

        logger.info(f"Movie like status for movie with id={movie_id}: {movie_like.is_liked}")
        return MovieLikeResponseSchema(
            is_liked=movie_like.is_liked,
            created_at=movie_like.created_at,
            user=user.id,
            movie=movie.id,
        )

    async def favorite_or_unfavorite(
        self, movie_id: int, user: UserModel
    ) -> MovieFavoriteResponseSchema:
        logger.info(f"User {user.id} favoriting or unfavoriting movie with id={movie_id}")
        movie = await self.repository.get_movie_by_id(movie_id)
        if not movie:
            logger.warning(f"Movie with id={movie_id} not found")
            raise HTTPException(
                status_code=404, detail="Movie with the given ID was not found."
            )

        movie_favorite = await self.repository.toggle_movie_favorite(movie, user.id)

        logger.info(f"Movie favorite status for movie with id={movie_id}: {movie_favorite.is_favorite}")
        return MovieFavoriteResponseSchema(
            is_favorite=movie_favorite.is_favorite,
            added_at=movie_favorite.added_at,
            user=user.id,
            movie=movie.id,
        )
