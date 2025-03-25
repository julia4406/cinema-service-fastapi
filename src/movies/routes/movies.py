from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.session_postgresql import get_postgresql_db as get_db
from src.movies.schemas.movies import (
    MovieListResponseSchema, MovieDetailSchema, MovieCreateSchema,
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
):
    return await MoviesService(db).get_movies(page=page, per_page=per_page)


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
