from src.config.logging_settings import logger
from src.database.exceptions.shopping_cart import CartItemError
from src.shopping_carts.dto.shopping_cart import CartItem, ShoppingCart
from src.shopping_carts.interfaces.repositories import AbstractCartRepository
from src.shopping_carts.interfaces.services import AbstractCartService


class CartService(AbstractCartService):
    def __init__(self, cart_repository: AbstractCartRepository) -> None:
        self._cart_repository = cart_repository

    async def get_cart(self, user_id: int) -> ShoppingCart:
        logger.info(f"Getting cart for user_id: {user_id}")
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            logger.info(
                f"Cart for user_id {user_id} does not exist, creating a new one."
            )
            cart = await self._cart_repository.create_cart(user_id)
        logger.info(f"Returning cart for user_id: {user_id}")
        return cart

    async def create_cart(self, user_id: int) -> ShoppingCart:
        logger.info(f"Creating cart for user_id: {user_id}")
        return await self._cart_repository.create_cart(user_id)

    async def add_item_to_cart(self, user_id: int, movie_id: int) -> CartItem:
        logger.info(
            f"Adding movie_id {movie_id} to cart for user_id: {user_id}"
        )
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            logger.info(
                f"Cart for user_id {user_id} does not exist, creating a new one."
            )
            cart = await self._cart_repository.create_cart(user_id)
        cart_item = await self._cart_repository.add_item_to_cart(
            cart.id,
            movie_id
        )
        logger.info(
            f"Movie with ID {movie_id} added to cart for user_id: {user_id}"
        )
        return cart_item

    async def remove_item_from_cart(self, item_id: int) -> None:
        logger.info(f"Removing item with item_id {item_id} from cart.")
        await self._cart_repository.remove_item_from_cart(item_id)
        logger.info(f"Item with item_id {item_id} removed from cart.")

    async def clear_cart(self, user_id: int) -> None:
        logger.info(f"Clearing cart for user_id: {user_id}")
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            logger.warning(
                f"Cart is empty or does not exist for user_id: {user_id}"
            )
            raise CartItemError("Cart is empty or does not exist")
        await self._cart_repository.clear_cart(cart.id)
        logger.info(f"Cart for user_id: {user_id} has been cleared.")

    async def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        logger.info(f"Fetching or creating cart for user_id: {user_id}")
        return await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

    async def add_item_to_cart_admin(
            self,
            user_id: int,
            movie_id: int
    ) -> ShoppingCart:
        logger.info(
            f"Adding movie_id {movie_id} to cart for user_id: {user_id}"
        )
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

        if any(item.movie_id == movie_id for item in cart.items):
            logger.warning(
                f"Movie with ID {movie_id} is already in cart for user_id: {user_id}"
            )
            raise CartItemError(f"Movie with ID {movie_id} is already in cart")

        await self._cart_repository.add_item_to_cart(cart.id, movie_id)
        updated_cart = await self._cart_repository.get_cart_by_user_id(user_id)
        logger.info(
            f"Movie with ID {movie_id} added to cart for user_id: {user_id}"
        )
        return updated_cart

    async def remove_item_from_cart_admin(
            self,
            user_id: int,
            movie_id: int
    ) -> ShoppingCart:
        logger.info(
            f"Removing movie_id {movie_id} from cart for user_id: {user_id}"
        )
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )

        for item in cart.items:
            if item.movie_id == movie_id:
                await self._cart_repository.remove_item_from_cart(item.id)
                logger.info(
                    f"Movie with ID {movie_id} removed from cart for user_id: {user_id}"
                )
                break
        updated_cart = await self._cart_repository.get_cart_by_user_id(user_id)
        return updated_cart

    async def clear_cart_admin(self, user_id: int) -> ShoppingCart:
        logger.info(f"Clearing cart for user_id: {user_id}")
        cart = await self._cart_repository.get_or_create_cart_by_user_id(
            user_id
        )
        await self._cart_repository.clear_cart(cart.id)
        updated_cart = await self._cart_repository.get_cart_by_user_id(user_id)
        logger.info(f"Cart for user_id: {user_id} has been cleared.")
        return updated_cart
