from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
from shopping_carts.dto.shopping_cart import CartItem, ShoppingCart, Purchase
from shopping_carts.interfaces.repositories import CartRepositoryInterface


class CartRepository(CartRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_cart(self, user_id: int) -> ShoppingCart:
        try:
            cart = ShoppingCartModel(user_id=user_id)
            self._session.add(cart)
            await self._session.flush()
            await self._session.refresh(cart)
            cart_dict = object_as_dict(cart)
            cart_dict["items"] = []
            return ShoppingCart(**cart_dict)
        except IntegrityError:
            await self._session.rollback()
            raise CreateCartError(
                f"Cart already exists for user with ID {user_id}"
            )
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CreateCartError(f"Failed to create cart: {str(e)}")

    async def get_cart_by_user_id(
            self,
            user_id: int
    ) -> Optional[ShoppingCart]:
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
        return ShoppingCart(**cart_dict)

    async def add_item_to_cart(self, cart_id: int, movie_id: int) -> CartItem:
        try:
            existing_item = await self._session.execute(
                select(CartItemModel).filter_by(
                    cart_id=cart_id,
                    movie_id=movie_id
                )
            )
            if existing_item.scalars().first():
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
            return cart_item_dto
        except (ValueError, SQLAlchemyError) as e:
            await self._session.rollback()
            if isinstance(e, ValueError):
                raise CartItemError(f"Cannot add movie to cart: {str(e)}")
            raise CartItemError(f"Failed to add item to cart: {str(e)}")

    async def remove_item_from_cart(self, cart_item_id: int) -> None:
        try:
            result = await self._session.execute(
                select(CartItemModel).filter_by(id=cart_item_id)
            )
            item = result.scalars().first()
            if item:
                await self._session.delete(item)
                await self._session.flush()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CartItemError(f"Failed to remove item from cart: {str(e)}")

    async def clear_cart(self, cart_id: int) -> None:
        try:
            result = await self._session.execute(
                select(CartItemModel).filter_by(cart_id=cart_id)
            )
            items = result.scalars().all()
            for item in items:
                await self._session.delete(item)
            await self._session.flush()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CartItemError(f"Failed to clear cart: {str(e)}")

    async def create_purchase(self, user_id: int, movie_id: int) -> Purchase:
        try:
            purchase = PurchasedModel(user_id=user_id, movie_id=movie_id)
            self._session.add(purchase)
            await self._session.flush()
            await self._session.refresh(purchase)
            return Purchase(**object_as_dict(purchase))
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CreatePurchaseError(f"Failed to create purchase: {str(e)}")

    async def get_user_purchases(self, user_id: int) -> List[Purchase]:
        result = await self._session.execute(
            select(PurchasedModel).filter_by(user_id=user_id)
        )
        purchases = result.scalars().all()
        return [Purchase(**object_as_dict(purchase)) for purchase in purchases]

    async def get_purchase_by_id(self, purchase_id: int) -> Optional[Purchase]:
        result = await self._session.execute(
            select(PurchasedModel).filter_by(id=purchase_id)
        )
        purchase = result.scalars().first()
        if not purchase:
            return None
        return Purchase(**object_as_dict(purchase))

    async def remove_purchase_by_id(self, purchase_id: int) -> None:
        try:
            result = await self._session.execute(
                select(PurchasedModel).filter_by(id=purchase_id)
            )
            purchase = result.scalars().first()
            if purchase:
                await self._session.delete(purchase)
                await self._session.flush()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CreatePurchaseError(f"Failed to remove purchase: {str(e)}")
