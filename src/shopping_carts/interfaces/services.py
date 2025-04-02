from abc import ABC, abstractmethod

from src.shopping_carts.dto.shopping_cart import ShoppingCart, CartItem


class AbstractCartService(ABC):

    @abstractmethod
    async def get_cart(self, user_id: int) -> ShoppingCart:
        pass

    @abstractmethod
    async def create_cart(self, user_id: int) -> ShoppingCart:
        pass

    @abstractmethod
    async def add_item_to_cart(self, user_id: int, movie_id: int) -> CartItem:
        pass

    @abstractmethod
    async def remove_item_from_cart(self, item_id: int) -> None:
        pass

    @abstractmethod
    async def clear_cart(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        pass

    @abstractmethod
    async def add_item_to_cart_admin(
            self,
            user_id: int,
            movie_id: int
            ) -> ShoppingCart:
        pass

    @abstractmethod
    async def remove_item_from_cart_admin(
            self,
            user_id: int,
            movie_id: int
            ) -> ShoppingCart:
        pass

    @abstractmethod
    async def clear_cart_admin(self, user_id: int) -> ShoppingCart:
        pass
