from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions.shopping_cart import (
    CreateCartError,
    CartItemError,
    CreatePurchaseError
)
from database.models.shopping_carts import (
    ShoppingCartModel,
    CartItemModel,
    PurchasedModel
)
from database.utils import object_as_dict
from shopping_carts.dto.shopping_cart import CartItem, ShoppingCart, Purchase
from shopping_carts.interfaces.repositories import CartRepositoryInterface


class CartRepository(CartRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_cart(self, user_id: int) -> ShoppingCart:
        try:
            async with self._session.begin():
                cart = ShoppingCartModel(user_id=user_id)
                self._session.add(cart)
                await self._session.flush()
                await self._session.refresh(cart)
                return ShoppingCart(**object_as_dict(cart))
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CreateCartError(f"Failed to create cart: {str(e)}")

    async def get_cart_by_user_id(
            self,
            user_id: int
    ) -> Optional[ShoppingCart]:
        result = await self._session.execute(
            select(ShoppingCartModel).filter_by(user_id=user_id)
        )
        cart = result.scalars().first()
        if not cart:
            return None

        cart_dict = object_as_dict(cart)
        cart_dict["items"] = [CartItem(**object_as_dict(item)) for item in
                              cart.items]
        return ShoppingCart(**cart_dict)

    async def add_item_to_cart(self, cart_id: int, movie_id: int) -> CartItem:
        try:
            async with self._session.begin():
                cart_item = CartItemModel(cart_id=cart_id, movie_id=movie_id)
                self._session.add(cart_item)
                await self._session.flush()
                await self._session.refresh(cart_item)
                return CartItem(**object_as_dict(cart_item))
        except ValueError as e:
            await self._session.rollback()
            raise CartItemError(f"Cannot add movie to cart: {str(e)}")
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CartItemError(f"Failed to add item to cart: {str(e)}")

    async def remove_item_from_cart(self, cart_item_id: int) -> None:
        try:
            async with self._session.begin():
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
            async with self._session.begin():
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
            async with self._session.begin():
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

    async def remove_purchase_by_id(self, movie_id: int) -> None:
        try:
            async with self._session.begin():
                result = await self._session.execute(
                    select(PurchasedModel).filter_by(movie_id=movie_id)
                )
                purchases = result.scalars().all()
                for purchase in purchases:
                    await self._session.delete(purchase)
                await self._session.flush()
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise CreatePurchaseError(
                f"Failed to remove purchases for movie {movie_id}: {str(e)}"
            )
