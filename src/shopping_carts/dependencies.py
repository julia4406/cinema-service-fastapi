from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from database.session_postgresql import get_postgresql_db
from shopping_carts.interfaces.services import CartServiceInterface
from shopping_carts.repositories.shopping_cart import CartRepository
from shopping_carts.services.shopping_cart import CartService


async def get_current_user() -> UserModel:
    return UserModel(id=1)


async def get_cart_service(
        db: AsyncSession = Depends(get_postgresql_db)
) -> CartServiceInterface:
    return CartService(CartRepository(db))
