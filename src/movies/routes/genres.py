from fastapi import APIRouter, Depends, Query

from src.accounts.dependencies import role_required
from src.database.models import UserGroupEnum
from src.database.models import UserModel
from src.movies.schemas.genres import (
    GenreSchema,
    GenresResponseSchema,
    GenreCreateSchema,
)
from src.movies.service.genres import GenresService, get_movies_service

router = APIRouter()


@router.get(
    "/genres/",
    response_model=GenresResponseSchema,
)
async def get_genres_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    service: GenresService = Depends(get_movies_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await service.get_genres(page, per_page)


@router.get(
    "/genres/{genre_id}/",
    response_model=GenreSchema,
)
async def get_genre(
    genre_id: int,
    service: GenresService = Depends(get_movies_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await service.get_one_genre(genre_id)


@router.post(
    "/genres/",
    status_code=201,
    response_model=GenreSchema,
)
async def create_genre(
    genre_data: GenreCreateSchema,
    service: GenresService = Depends(get_movies_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await service.create_genre(genre_data)


@router.put(
    "/genres/{genre_id}/",
    status_code=200,
)
async def update_genre(
    genre_id: int,
    new_genre: GenreCreateSchema,
    service: GenresService = Depends(get_movies_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await service.update_genre(genre_id, new_genre)


@router.delete("/genres/{genre_id}/", status_code=204)
async def delete_genre(
    genre_id: int,
    service: GenresService = Depends(get_movies_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await service.delete_genre(genre_id)
