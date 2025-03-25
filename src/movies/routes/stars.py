from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_postgresql import get_postgresql_db as get_db
from movies.schemas.stars import StarsResponseSchema, StarSchema, StarCreateSchema
from movies.service.stars import StarsService

router = APIRouter()


@router.get(
    "/stars/",
    response_model=StarsResponseSchema,
)
async def get_stars_list(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=100)
):
    return await StarsService(db).get_stars(page, per_page)


@router.get(
    "/stars/{star_id}/",
    response_model=StarSchema,
)
async def get_star(star_id: int, db: AsyncSession = Depends(get_db)):
    return await StarsService(db).get_one_star(star_id)


@router.post(
    "/stars/",
    status_code=201,
    response_model=StarSchema,
)
async def create_star(
        star_data: StarCreateSchema,
        db: AsyncSession = Depends(get_db)
):
    return await StarsService(db).create_star(star_data)


@router.put(
    "/stars/{star_id}/",
    status_code=200,
)
async def update_star(
        star_id: int,
        new_star: StarCreateSchema,
        db: AsyncSession = Depends(get_db),
):
    return await StarsService(db).update_star(star_id, new_star)


@router.delete("/stars/{star_id}/", status_code=204)
async def delete_star(star_id: int, db: AsyncSession = Depends(get_db)):
    return await StarsService(db).delete_star(star_id)
