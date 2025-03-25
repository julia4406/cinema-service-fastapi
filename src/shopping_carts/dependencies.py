from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_postgresql import get_transactional_db
from shopping_carts.interfaces.services import CartServiceInterface
from shopping_carts.repositories.shopping_cart import CartRepository
from shopping_carts.services.shopping_cart import CartService


async def get_cart_service(
        db: AsyncSession = Depends(get_transactional_db)
) -> CartServiceInterface:
    return CartService(CartRepository(db))
