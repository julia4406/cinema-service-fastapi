from typing import List, Optional, Tuple
from datetime import datetime

from src.database.models import StatusEnum
from src.orders.dto.orders import Order
from src.orders.interfaces.repositories import OrderRepositoryInterface
from src.orders.interfaces.services import AdminOrderServiceInterface
from src.shopping_carts.interfaces.repositories import CartRepositoryInterface
from sqlalchemy.ext.asyncio import AsyncSession


class AdminOrderService(AdminOrderServiceInterface):
    def __init__(
            self,
            order_repository: OrderRepositoryInterface,
            cart_repository: CartRepositoryInterface,
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
        return await self._order_repository.get_all_orders(
            user_id, date_from, date_to, status, limit, offset
        )

    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        await self._order_repository.update_order_status(order_id, status)
        return await self._order_repository.get_order_by_id(order_id)
