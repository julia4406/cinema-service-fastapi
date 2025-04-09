from fastapi import APIRouter, Depends, Query

from src.accounts.dependencies import role_required
from src.database.models import UserGroupEnum, UserModel
from src.movies.schemas.stars import StarCreateSchema, StarSchema, StarsResponseSchema
from src.movies.service.stars import StarsService, get_stars_service

router = APIRouter()


@router.get(
    "/stars/",
    response_model=StarsResponseSchema,
)
async def get_stars_list(
    service: StarsService = Depends(get_stars_service),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
):
    return await service.get_stars(page, per_page)


@router.get(
    "/stars/{star_id}/",
    response_model=StarSchema,
)
async def get_star(
    star_id: int,
    service: StarsService = Depends(get_stars_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
):
    return await service.get_one_star(star_id)


@router.post(
    "/stars/",
    status_code=201,
    response_model=StarSchema,
)
async def create_star(
    star_data: StarCreateSchema,
    service: StarsService = Depends(get_stars_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await service.create_star(star_data)


@router.put(
    "/stars/{star_id}/",
    status_code=200,
)
async def update_star(
    star_id: int,
    new_star: StarCreateSchema,
    service: StarsService = Depends(get_stars_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
):
    return await service.update_star(star_id, new_star)


@router.delete("/stars/{star_id}/", status_code=204)
async def delete_star(
    star_id: int,
    service: StarsService = Depends(get_stars_service),
    current_user: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
):
    return await service.delete_star(star_id)
