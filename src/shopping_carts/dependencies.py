from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shopping_carts.interfaces.repositories import AbstractCartRepository
from src.shopping_carts.interfaces.services import AbstractCartService
from src.shopping_carts.services.shopping_cart import CartService
from src.database.session_postgresql import get_transactional_db
from src.shopping_carts.repositories.shopping_cart import CartRepository


async def get_cart_repository() -> AbstractCartRepository:
    db: AsyncSession = await get_transactional_db()
    return CartRepository(db)


async def get_cart_service(
        cart_repo: AbstractCartRepository = Depends(get_cart_repository)
) -> AbstractCartService:
    return CartService(cart_repo)


async def get_admin_cart_service(
        cart_repo: AbstractCartRepository = Depends(get_cart_repository)
) -> AbstractCartService:
    return CartService(cart_repo)
