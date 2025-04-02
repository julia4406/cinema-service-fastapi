from typing import List, Optional, Tuple
from datetime import datetime

from shopping_carts.interfaces.repositories import AbstractCartRepository
from src.database.models import StatusEnum
from src.orders.dto.orders import Order
from src.orders.interfaces.repositories import OrderRepositoryInterface
from src.orders.interfaces.services import AdminOrderServiceInterface
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.logging_settings import logger


class AdminOrderService(AdminOrderServiceInterface):
    def __init__(
            self,
            order_repository: OrderRepositoryInterface,
            cart_repository: AbstractCartRepository,
            session: AsyncSession
    ):
        self._order_repository = order_repository
        self._cart_repository = cart_repository
        self._session = session

    async def get_all_orders(
            self,
            user_id: Optional[int] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            status: Optional[StatusEnum] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[Order], int]:
        logger.info(
            f"Fetching all orders with filters: user_id={user_id}, date_from={date_from}, date_to={date_to}, status={status}, limit={limit}, offset={offset}"
        )
        orders, total = await self._order_repository.get_all_orders(
            user_id, date_from, date_to, status, limit, offset
        )
        logger.info(f"Fetched {len(orders)} orders, total count: {total}")
        return orders, total

    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> Order:
        logger.info(
            f"Updating order status for order_id: {order_id} to {status}"
        )
        order = await self._order_repository.get_order_by_id(order_id)
        if not order:
            logger.warning(f"Order with order_id {order_id} not found")
            raise ValueError("Order not found")
        await self._order_repository.update_order_status(order_id, status)
        updated_order = await self._order_repository.get_order_by_id(order_id)
        logger.info(
            f"Order status for order_id {order_id} updated to {status}"
        )
        return updated_order
