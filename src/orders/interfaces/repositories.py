from abc import ABC, abstractmethod
from typing import List, Optional

from src.database.models import StatusEnum
from src.orders.dto.orders import Order
from src.shopping_carts.dto.shopping_cart import CartItem


class OrderRepositoryInterface(ABC):
    @abstractmethod
    async def create_order(
            self,
            user_id: int,
            cart_items: List[CartItem]
    ) -> Order:
        pass

    @abstractmethod
    async def get_orders_by_user_id(self, user_id: int) -> List[Order]:
        pass

    @abstractmethod
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> None:
        pass
