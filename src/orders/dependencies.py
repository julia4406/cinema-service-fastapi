from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.orders.services.admin import AdminOrderService
from src.database.session_postgresql import get_transactional_db
from src.orders.interfaces.services import (
    OrderServiceInterface,
    AdminOrderServiceInterface
)
from src.orders.repositories.orders import OrderRepository
from src.orders.services.orders import OrderService
from src.shopping_carts.repositories.shopping_cart import CartRepository


async def get_order_repository(
        db: AsyncSession = Depends(get_transactional_db)
) -> OrderRepository:
    return OrderRepository(db)


async def get_cart_repository(
        db: AsyncSession = Depends(get_transactional_db)
) -> CartRepository:
    return CartRepository(db)


async def get_order_service(
        order_repo: OrderRepository = Depends(get_order_repository),
        cart_repo: CartRepository = Depends(get_cart_repository),
        db: AsyncSession = Depends(get_transactional_db)
) -> OrderServiceInterface:
    return OrderService(order_repo, cart_repo, db)


async def get_admin_order_service(
        order_repo: OrderRepository = Depends(get_order_repository),
        cart_repo: CartRepository = Depends(get_cart_repository),
        db: AsyncSession = Depends(get_transactional_db)
) -> AdminOrderServiceInterface:
    return AdminOrderService(order_repo, cart_repo, db)
