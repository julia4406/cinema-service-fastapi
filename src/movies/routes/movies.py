from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.session_postgresql import get_postgresql_db as get_db
from src.movies.schemas.movies import (
    MovieListResponseSchema,
)
from src.movies.service.movies import MoviesService

router = APIRouter()


@router.get(
    "/",
    response_model=MovieListResponseSchema,
    summary="Get a paginated list of movies with optional "
            "filtering and sorting"
)
async def get_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    return await MoviesService(db).get_movies(page=page, per_page=per_page)
