from fastapi import APIRouter
from movies.routes.genres import router as genres_router
from movies.routes.stars import router as stars_router

router = APIRouter(prefix="/theater")
router.include_router(genres_router)
router.include_router(stars_router)
