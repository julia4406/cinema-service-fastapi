from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import UserModel
from src.database.session_postgresql import get_postgresql_db as get_db
from src.movies.schemas.genres import (
    GenreSchema,
    GenresResponseSchema,
    GenreCreateSchema,
)
from src.movies.service.genres import GenresService
from src.accounts.dependencies import role_required
from src.database.models import UserGroupEnum

router = APIRouter()


@router.get(
    "/genres/",
    response_model=GenresResponseSchema,
)
async def get_genres_list(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await GenresService(db).get_genres(page, per_page)


@router.get(
    "/genres/{genre_id}/",
    response_model=GenreSchema,
)
async def get_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await GenresService(db).get_one_genre(genre_id)


@router.post(
    "/genres/",
    status_code=201,
    response_model=GenreSchema,
)
async def create_genre(
    genre_data: GenreCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await GenresService(db).create_genre(genre_data)


@router.put(
    "/genres/{genre_id}/",
    status_code=200,
)
async def update_genre(
    genre_id: int,
    new_genre: GenreCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await GenresService(db).update_genre(genre_id, new_genre)


@router.delete("/genres/{genre_id}/", status_code=204)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await GenresService(db).delete_genre(genre_id)
