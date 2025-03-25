from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session_postgresql import get_transactional_db
from src.orders.interfaces.services import OrderServiceInterface
from src.orders.repositories.orders import OrderRepository
from src.orders.services.orders import OrderService
from src.shopping_carts.repositories.shopping_cart import CartRepository


async def get_order_service(
        db: AsyncSession = Depends(get_transactional_db)
) -> OrderServiceInterface:
    cart_repository = CartRepository(db)
    order_repository = OrderRepository(db)
    return OrderService(order_repository, cart_repository, db)
