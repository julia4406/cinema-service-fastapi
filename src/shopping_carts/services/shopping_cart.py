from shopping_carts.dto.shopping_cart import ShoppingCart, CartItem
from shopping_carts.interfaces.repositories import CartRepositoryInterface
from shopping_carts.interfaces.services import CartServiceInterface


class CartService(CartServiceInterface):
    def __init__(self, cart_repository: CartRepositoryInterface):
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
