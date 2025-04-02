from src.shopping_carts.dto.shopping_cart import ShoppingCart, CartItem
from src.shopping_carts.interfaces.repositories import AbstractCartRepository
from src.shopping_carts.interfaces.services import AbstractCartService


class CartService(AbstractCartService):
    def __init__(self, cart_repository: AbstractCartRepository):
        self._cart_repository = cart_repository

    async def get_cart(self, user_id: int) -> ShoppingCart:
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            cart = await self._cart_repository.create_cart(user_id)
        return cart

    async def create_cart(self, user_id: int) -> ShoppingCart:
        return await self._cart_repository.create_cart(user_id)

    async def add_item_to_cart(self, user_id: int, movie_id: int) -> CartItem:
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            cart = await self._cart_repository.create_cart(user_id)
        return await self._cart_repository.add_item_to_cart(cart.id, movie_id)

    async def remove_item_from_cart(self, item_id: int) -> None:
        await self._cart_repository.remove_item_from_cart(item_id)

    async def clear_cart(self, user_id: int) -> None:
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty or does not exist")
        await self._cart_repository.clear_cart(cart.id)

    async def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        return await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

    async def add_item_to_cart_admin(
            self,
            user_id: int,
            movie_id: int
    ) -> ShoppingCart:
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

        if any(item.movie_id == movie_id for item in cart.items):
            raise ValueError(f"Movie with ID {movie_id} is already in cart")
        await self._cart_repository.add_item_to_cart(cart.id, movie_id)
        return await self._cart_repository.get_cart_by_user_id(user_id)

    async def remove_item_from_cart_admin(
            self,
            user_id: int,
            movie_id: int
    ) -> ShoppingCart:
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

        for item in cart.items:
            if item.movie_id == movie_id:
                await self._cart_repository.remove_item_from_cart(item.id)
                break
        return await self._cart_repository.get_cart_by_user_id(user_id)

    async def clear_cart_admin(self, user_id: int) -> ShoppingCart:
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )
        await self._cart_repository.clear_cart(cart.id)
        return await self._cart_repository.get_cart_by_user_id(user_id)
