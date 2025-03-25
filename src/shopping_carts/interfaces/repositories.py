from abc import ABC, abstractmethod
from typing import List, Optional

from src.shopping_carts.dto.shopping_cart import (
    ShoppingCart,
    CartItem,
    Purchase
)


class CartRepositoryInterface(ABC):

    @abstractmethod
    async def create_cart(self, user_id: int) -> ShoppingCart:
        pass

    @abstractmethod
    async def get_cart_by_user_id(
            self,
            user_id: int
    ) -> Optional[ShoppingCart]:
        pass

    @abstractmethod
    async def add_item_to_cart(self, cart_id: int, movie_id: int) -> CartItem:
        pass

    @abstractmethod
    async def remove_item_from_cart(self, cart_item_id: int) -> None:
        pass

    @abstractmethod
    async def clear_cart(self, cart_id: int) -> None:
        pass

    @abstractmethod
    async def create_purchase(self, user_id: int, movie_id: int) -> Purchase:
        pass

    @abstractmethod
    async def get_user_purchases(self, user_id: int) -> List[Purchase]:
        pass

    @abstractmethod
    async def get_purchase_by_id(self, purchase_id: int) -> Optional[Purchase]:
        pass

    @abstractmethod
    async def remove_purchase_by_id(self, purchase_id: int) -> None:
        pass
