from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.dependencies import get_current_user
from database.session_postgresql import get_postgresql_db as get_db
from src.database.models.accounts import UserModel
from src.movies.schemas.movies import (
    MovieListResponseSchema, MovieDetailSchema, MovieCreateSchema, MovieUpdateSchema, DetailMessageSchema,
    MovieLikeResponseSchema, MovieFavoriteResponseSchema, MovieSortEnum, FavoriteMoviesSchema,
)
from src.movies.service.movies import MoviesService

router = APIRouter()


@router.get(
    "/",
    response_model=MovieListResponseSchema,
    summary="Get list of movies"
)
async def get_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search_title: Optional[str] = Query(
        None,
        description="Search by title or description"
    ),
    search_person: Optional[str] = Query(
        None,
        description="Search by actor or director"
    ),
    year: Optional[int] = Query(
        None,
        description="Filter by release year"
    ),
    min_imdb: Optional[float] = Query(
        None,
        description="Filter by minimum IMDb rating"
    ),
    max_imdb: Optional[float] = Query(
        None,
        description="Filter by maximum IMDb rating"
    ),
    min_price: Optional[float] = Query(
        None,
        description="Filter by minimum price"
    ),
    max_price: Optional[float] = Query(
        None,
        description="Filter by maximum price"
    ),
    sort_by: Optional[MovieSortEnum] = Query(
        None,
        description="Sort movies by criteria"
    ),
):
    filters = {
        "name": search_title,
        "search_person": search_person,
        "year": year,
        "min_imdb": min_imdb,
        "max_imdb": max_imdb,
        "min_price": min_price,
        "max_price": max_price,
    }

    return await MoviesService(db).get_movies(
        page=page, per_page=per_page,
        filters=filters, sort_by=sort_by
    )


@router.get(
    "/{id}",
    response_model=MovieDetailSchema,
)
async def get_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db)
):
    return await MoviesService(db).get_movie_by_id(movie_id)


@router.post(
    "/",
    response_model=MovieDetailSchema,
    status_code=201,
    summary="Create a new movie",
)
async def create_movie(
        movie_data: MovieCreateSchema,
        db: AsyncSession = Depends(get_db),
):
    return await MoviesService(db).create_movie(movie_data)


@router.patch(
    "/{id}",
    response_model=DetailMessageSchema,
    summary="Update movie by ID",
    status_code=200,
    responses={
        200: {
            "description": "Movie updated successfully.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie updated successfully."}
                }
            },
        },
        400: {
            "description": "Invalid input data.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid input data."}
                }
            },
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie not found."}
                }
            },
        },
    },
)
async def update_movie(
        movie_id: int,
        movie_data: MovieUpdateSchema,
        db: AsyncSession = Depends(get_db),
) -> DetailMessageSchema:
    return await MoviesService(db).update_movie(movie_id, movie_data)


@router.delete(
    "/{movie_id}/",
    summary="Delete a movie by ID",
    status_code=204,
    responses={
        204: {
            "description": "Movie deleted successfully."
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Movie with the given ID was not found."
                    }
                }
            },
        },
    },
)
async def delete_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
) -> None:
    return await MoviesService(db).delete_movie(movie_id)


@router.post(
    "/{movie_id}/like/",
    response_model=MovieLikeResponseSchema,
    summary="Like or dislike a movie",
    responses={
        200: {"description": "Movie like status updated."},
        404: {
            "description": "Movie or user not found.",
            "content": {
                "application/json":
                    {
                        "example": {
                            "detail": "Movie with the given ID was not found."
                        }
                    }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content":
                {
                    "application/json":
                        {
                            "example":
                                {
                                    "detail": "Invalid or expired token."
                                }
                        }
                }
        },
    }
)
async def like_or_dislike(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
) -> MovieLikeResponseSchema:
    return await MoviesService(db).like_or_dislike_movie(movie_id, user)


@router.post(
    "/{movie_id}/favorite/",
    response_model=MovieFavoriteResponseSchema,
    summary="Add or remove a movie from favorites",
    responses={
        200: {"description": "Movie favorite status updated."},
        404: {
            "description": "Movie or user not found.",
            "content": {
                "application/json":
                    {
                        "example": {
                            "detail": "Movie with the given ID was not found."
                        }
                    }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content":
                {
                    "application/json":
                        {
                            "example":
                                {
                                    "detail": "Invalid or expired token."
                                }
                        }
                }
        },
    }
)
async def favorite_or_unfavorite(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserModel = Depends(get_current_user)
) -> MovieFavoriteResponseSchema:
    return await MoviesService(db).favorite_or_unfavorite(movie_id, user)


@router.get(
    "/favorites/",
    response_model=FavoriteMoviesSchema,
)
async def favorites(
page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search_title: Optional[str] = Query(
        None,
        description="Search by title or description"
    ),
    search_person: Optional[str] = Query(
        None,
        description="Search by actor or director"
    ),
    year: Optional[int] = Query(
        None,
        description="Filter by release year"
    ),
    min_imdb: Optional[float] = Query(
        None,
        description="Filter by minimum IMDb rating"
    ),
    max_imdb: Optional[float] = Query(
        None,
        description="Filter by maximum IMDb rating"
    ),
    min_price: Optional[float] = Query(
        None,
        description="Filter by minimum price"
    ),
    max_price: Optional[float] = Query(
        None,
        description="Filter by maximum price"
    ),
    sort_by: Optional[MovieSortEnum] = Query(
        None,
        description="Sort movies by criteria"
    ),
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user)
) -> FavoriteMoviesSchema:
    filters = {
        "name": search_title,
        "search_person": search_person,
        "year": year,
        "min_imdb": min_imdb,
        "max_imdb": max_imdb,
        "min_price": min_price,
        "max_price": max_price,
    }

    return await MoviesService(db).get_movies(
        page=page, per_page=per_page,
        filters=filters, sort_by=sort_by,
        user=user
    )
