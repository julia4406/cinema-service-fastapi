from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions.orders import CreateOrderError, OrderUpdateError
from src.database.models import StatusEnum
from src.database.models.movies import MovieModel
from src.orders.dto.orders import Order
from src.orders.interfaces.repositories import OrderRepositoryInterface
from src.orders.interfaces.services import OrderServiceInterface
from src.shopping_carts.interfaces.repositories import AbstractCartRepository


class OrderService(OrderServiceInterface):
    def __init__(
            self,
            order_repository: OrderRepositoryInterface,
            cart_repository: AbstractCartRepository,
            session: AsyncSession
    ):
        self._order_repository = order_repository
        self._cart_repository = cart_repository
        self._session = session

    async def create_order(self, user_id: int) -> Order:
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            raise CreateOrderError("Cart is empty or does not exist")

        purchases = await self._cart_repository.get_user_purchases(user_id)
        purchased_movie_ids = {purchase.movie_id for purchase in purchases}
        cart_movie_ids = {item.movie_id for item in cart.items}
        if purchased_movie_ids & cart_movie_ids:
            raise CreateOrderError("Some movies are already purchased")

        movie_ids = [item.movie_id for item in cart.items]
        result = await self._session.execute(
            select(MovieModel).filter(MovieModel.id.in_(movie_ids))
        )
        available_movies = result.scalars().all()
        if len(available_movies) != len(movie_ids):
            raise CreateOrderError("Some movies are not available")

        order = await self._order_repository.create_order(user_id, cart.items)

        await self._cart_repository.clear_cart(cart.id)

        return order

    async def get_user_orders(self, user_id: int) -> List[Order]:
        orders = await self._order_repository.get_orders_by_user_id(user_id)
        return orders

    async def get_order(self, user_id: int, order_id: int) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderUpdateError(
                "Order not found or does not belong to user"
            )
        return order

    async def cancel_pending_order(self, user_id: int, order_id: int) -> None:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderUpdateError(
                "Order not found or does not belong to user"
            )
        if order.status != StatusEnum.PENDING:
            raise OrderUpdateError(
                "Only pending orders can be cancelled by user"
            )
        await self._order_repository.update_order_status(
            order_id,
            StatusEnum.CANCELLED
        )

    async def confirm_order(self, user_id: int, order_id: int) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderUpdateError(
                "Order not found or does not belong to user"
            )
        if order.status != StatusEnum.PENDING:
            raise OrderUpdateError("Only pending orders can be confirmed")

        movie_ids = [item.movie_id for item in order.items]
        result = await self._session.execute(
            select(MovieModel).filter(MovieModel.id.in_(movie_ids))
        )
        current_movies = result.scalars().all()
        current_total = sum(movie.price for movie in current_movies)
        if current_total != order.total_amount:
            order.total_amount = current_total

        await self._order_repository.update_order_status(
            order_id,
            StatusEnum.PAID
        )

        return await self._order_repository.get_order_by_id(order_id)

    async def get_all_orders(
            self,
            user_id: Optional[int] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            status: Optional[StatusEnum] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[Order], int]:
        return await self._order_repository.get_all_orders(
            user_id, date_from, date_to, status, limit, offset
        )

    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order:
            raise OrderUpdateError("Order not found")
        await self._order_repository.update_order_status(order_id, status)
        return await self._order_repository.get_order_by_id(order_id)
