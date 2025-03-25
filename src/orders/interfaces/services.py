from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

from database.models import StatusEnum
from orders.dto.orders import Order


class OrderServiceInterface(ABC):
    @abstractmethod
    async def create_order(self, user_id: int) -> Order:
        pass

    @abstractmethod
    async def get_user_orders(self, user_id: int) -> List[Order]:
        pass

    @abstractmethod
    async def get_order(self, user_id: int, order_id: int) -> Order:
        pass

    @abstractmethod
    async def cancel_pending_order(self, user_id: int, order_id: int) -> None:
        pass

    @abstractmethod
    async def confirm_order(self, user_id: int, order_id: int) -> Order:
        pass

    @abstractmethod
    async def get_all_orders(
            self,
            user_id: Optional[int] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            status: Optional[StatusEnum] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[Order], int]:
        pass


class AdminOrderServiceInterface(ABC):
    @abstractmethod
    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> Order:
        pass
