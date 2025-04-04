from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config.logging_settings import logger
from src.database.exceptions.shopping_cart import (
    CreateCartError,
    CartItemError,
    CreatePurchaseError
)
from src.database.models import (
    ShoppingCartModel,
    CartItemModel,
    PurchasedModel, MovieModel
)
from src.database.utils import object_as_dict
from src.shopping_carts.dto.shopping_cart import (
    CartItem,
    ShoppingCart,
    Purchase
)
from src.shopping_carts.interfaces.repositories import AbstractCartRepository


class CartRepository(AbstractCartRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_cart(self, user_id: int) -> ShoppingCart:
        try:
            logger.info(f"Attempting to create a shopping cart for user_id: {user_id}")
            cart = ShoppingCartModel(user_id=user_id)
            self._session.add(cart)
            await self._session.flush()
            await self._session.refresh(cart)
            cart_dict = object_as_dict(cart)
            cart_dict["items"] = []
            logger.info(f"Cart successfully created for user_id: {user_id}")
            return ShoppingCart(**cart_dict)
        except IntegrityError:
            await self._session.rollback()
            logger.error(
                f"Cart creation failed: Cart already exists for user_id: {user_id}")
            raise CreateCartError(
                f"Cart already exists for user with ID {user_id}"
            )
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Failed to create cart for user_id: {user_id}. Error: {str(e)}")
            raise CreateCartError(f"Failed to create cart: {str(e)}")

    async def get_cart_by_user_id(
            self,
            user_id: int
    ) -> Optional[ShoppingCart]:
        try:
            logger.info(f"Fetching cart for user_id: {user_id}")
            result = await self._session.execute(
                select(ShoppingCartModel)
                .filter_by(user_id=user_id)
                .options(
                    joinedload(ShoppingCartModel.items)
                    .joinedload(CartItemModel.movie)
                    .joinedload(MovieModel.genres)
                )
            )
            cart = result.scalars().first()
            if not cart:
                logger.warning(f"No cart found for user_id: {user_id}")
                return None
            cart_dict = object_as_dict(cart)
            cart_dict["items"] = [
                CartItem(
                    **{
                        **object_as_dict(item),
                        "name": item.movie.name,
                        "price": item.movie.price,
                        "genres": item.movie.genres,
                        "year": item.movie.year,
                    }
                )
                for item in cart.items
            ]
            logger.info(f"Cart fetched successfully for user_id: {user_id}")
            return ShoppingCart(**cart_dict)
        except SQLAlchemyError as e:
            raise CartItemError(f"Failed to retrieve cart: {str(e)}")

    async def get_or_create_cart_by_user_id(
            self,
            user_id: int
    ) -> ShoppingCart:
        logger.info(f"Checking if cart exists for user_id: {user_id}")
        cart = await self.get_cart_by_user_id(user_id)
        if not cart:
            logger.info(f"No cart found for user_id: {user_id}, creating a new one.")
            cart = await self.create_cart(user_id)
        return cart

    async def add_item_to_cart(self, cart_id: int, movie_id: int) -> CartItem:
        try:
            logger.info(f"Attempting to add movie_id: {movie_id} to cart_id: {cart_id}")
            existing_item = await self._session.execute(
                select(CartItemModel).filter_by(
                    cart_id=cart_id,
                    movie_id=movie_id
                )
            )
            if existing_item.scalars().first():
                logger.warning(f"Movie with ID {movie_id} already exists in cart {cart_id}")
                raise CartItemError(
                    f"Movie with ID {movie_id} is already in cart with ID {cart_id}"
                )

            cart_item = CartItemModel(cart_id=cart_id, movie_id=movie_id)
            self._session.add(cart_item)
            await self._session.flush()

            result = await self._session.execute(
                select(CartItemModel)
                .filter_by(id=cart_item.id)
                .options(
                    joinedload(CartItemModel.movie).joinedload(
                        MovieModel.genres
                    )
                )
            )
            cart_item = result.scalars().first()

            if not cart_item:
                logger.error("Failed to retrieve cart item after creation")
                raise CartItemError(
                    "Failed to retrieve cart item after creation"
                )

            movie = cart_item.movie
            item_dict = object_as_dict(cart_item)
            item_dict.update(
                {
                    "name": movie.name if movie else None,
                    "price": movie.price if movie else None,
                    "genres": [genre.name for genre in
                               movie.genres] if movie and movie.genres else None,
                    "year": movie.year if movie else None,
                }
            )
            cart_item_dto = CartItem(**item_dict)
            logger.info(f"Movie ID {movie_id} successfully added to cart ID {cart_id}")
            return cart_item_dto
        except (ValueError, SQLAlchemyError) as e:
            await self._session.rollback()
            logger.error(f"Failed to add item to cart with cart_id: {cart_id}, movie_id: {movie_id}. Error: {str(e)}")
            if isinstance(e, ValueError):
                raise CartItemError(f"Cannot add movie to cart: {str(e)}")
            raise CartItemError(f"Failed to add item to cart: {str(e)}")

    async def remove_item_from_cart(self, cart_item_id: int) -> None:
        try:
            logger.info(f"Attempting to remove item with cart_item_id: {cart_item_id}")
            result = await self._session.execute(
                select(CartItemModel).filter_by(id=cart_item_id)
            )
            item = result.scalars().first()
            if item:
                await self._session.delete(item)
                await self._session.flush()
                logger.info(f"Item with cart_item_id: {cart_item_id} successfully removed from cart")
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Failed to remove item with cart_item_id: {cart_item_id}. Error: {str(e)}")
            raise CartItemError(f"Failed to remove item from cart: {str(e)}")

    async def clear_cart(self, cart_id: int) -> None:
        try:
            logger.info(f"Attempting to clear cart with cart_id: {cart_id}")
            result = await self._session.execute(
                select(CartItemModel).filter_by(cart_id=cart_id)
            )
            items = result.scalars().all()
            for item in items:
                await self._session.delete(item)
            await self._session.flush()
            logger.info(f"Cart with cart_id: {cart_id} successfully cleared")
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Failed to clear cart with cart_id: {cart_id}. Error: {str(e)}")
            raise CartItemError(f"Failed to clear cart: {str(e)}")

    async def create_purchase(self, user_id: int, movie_id: int) -> Purchase:
        try:
            logger.info(f"Creating purchase for user_id: {user_id}, movie_id: {movie_id}")
            purchase = PurchasedModel(user_id=user_id, movie_id=movie_id)
            self._session.add(purchase)
            await self._session.flush()
            await self._session.refresh(purchase)
            logger.info(f"Purchase created successfully for user_id: {user_id}, movie_id: {movie_id}")
            return Purchase(**object_as_dict(purchase))
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Failed to create purchase for user_id: {user_id}, movie_id: {movie_id}. Error: {str(e)}")
            raise CreatePurchaseError(f"Failed to create purchase: {str(e)}")

    async def get_user_purchases(self, user_id: int) -> List[Purchase]:
        try:
            logger.info(f"Fetching purchases for user_id: {user_id}")
            result = await self._session.execute(
                select(PurchasedModel).filter_by(user_id=user_id)
            )
            purchases = result.scalars().all()
            logger.info(
                f"Found {len(purchases)} purchases for user_id: {user_id}")
            return [Purchase(**object_as_dict(purchase)) for purchase in
                    purchases]
        except SQLAlchemyError as e:
            raise CreatePurchaseError(
                f"Failed to retrieve purchases: {str(e)}"
            )

    async def get_purchase_by_id(self, purchase_id: int) -> Optional[Purchase]:
        try:
            logger.info(f"Fetching purchase by purchase_id: {purchase_id}")
            result = await self._session.execute(
                select(PurchasedModel).filter_by(id=purchase_id)
            )
            purchase = result.scalars().first()
            if not purchase:
                logger.warning(f"Purchase not found for purchase_id: {purchase_id}")
                return None
            logger.info(f"Purchase found for purchase_id: {purchase_id}")
            return Purchase(**object_as_dict(purchase))
        except SQLAlchemyError as e:
            raise CreatePurchaseError(f"Failed to retrieve purchase: {str(e)}")

    async def remove_purchase_by_id(self, purchase_id: int) -> None:
        try:
            logger.info(f"Attempting to remove purchase with purchase_id: {purchase_id}")
            result = await self._session.execute(
                select(PurchasedModel).filter_by(id=purchase_id)
            )
            purchase = result.scalars().first()
            if purchase:
                await self._session.delete(purchase)
                await self._session.flush()
                logger.info(f"Purchase with purchase_id: {purchase_id} successfully removed")
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Failed to remove purchase with purchase_id: {purchase_id}. Error: {str(e)}")
            raise CreatePurchaseError(f"Failed to remove purchase: {str(e)}")
