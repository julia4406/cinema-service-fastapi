from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.session_postgresql import get_postgresql_db as get_db
from movies.schemas.stars import StarsResponseSchema
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
