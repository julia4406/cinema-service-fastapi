from abc import ABC, abstractmethod
from typing import List

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
    async def cancel_paid_order(self, user_id: int, order_id: int) -> None:
        pass

    @abstractmethod
    async def confirm_order(self, user_id: int, order_id: int) -> Order:
        pass
