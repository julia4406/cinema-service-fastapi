from fastapi import APIRouter
from src.movies.routes.genres import router as genres_router
from src.movies.routes.stars import router as stars_router
from src.movies.routes.movies import router as movies_router

router = APIRouter()
router.include_router(genres_router)
router.include_router(stars_router)
router.include_router(movies_router)
