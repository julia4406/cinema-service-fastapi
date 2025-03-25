from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import StatusEnum
from src.database.models.movies import MovieModel
from src.orders.dto.orders import Order
from src.orders.interfaces.repositories import OrderRepositoryInterface
from src.orders.interfaces.services import OrderServiceInterface
from src.shopping_carts.interfaces.repositories import CartRepositoryInterface


class OrderService(OrderServiceInterface):
    def __init__(
            self,
            order_repository: OrderRepositoryInterface,
            cart_repository: CartRepositoryInterface,
            session: AsyncSession
    ):
        self._order_repository = order_repository
        self._cart_repository = cart_repository
        self._session = session

    async def create_order(self, user_id: int) -> Order:
        # Получаем корзину
        cart = await self._cart_repository.get_cart_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty or does not exist")

        # Проверяем, что фильмы не куплены
        purchases = await self._cart_repository.get_user_purchases(user_id)
        purchased_movie_ids = {purchase.movie_id for purchase in purchases}
        cart_movie_ids = {item.movie_id for item in cart.items}
        if purchased_movie_ids & cart_movie_ids:
            raise ValueError("Some movies are already purchased")

        # Проверяем наличие фильмов в базе
        movie_ids = [item.movie_id for item in cart.items]
        result = await self._session.execute(
            select(MovieModel).filter(MovieModel.id.in_(movie_ids))
        )
        available_movies = result.scalars().all()
        if len(available_movies) != len(movie_ids):
            raise ValueError("Some movies are not available")

        # Создаем заказ
        order = await self._order_repository.create_order(user_id, cart.items)

        # Очищаем корзину после создания заказа
        await self._cart_repository.clear_cart(cart.id)

        return order

    async def get_user_orders(self, user_id: int) -> List[Order]:
        orders = await self._order_repository.get_orders_by_user_id(user_id)
        return orders

    async def get_order(self, user_id: int, order_id: int) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to user")
        return order

    async def cancel_pending_order(self, user_id: int, order_id: int) -> None:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to user")
        if order.status != StatusEnum.PENDING:
            raise ValueError("Only pending orders can be cancelled by user")
        await self._order_repository.update_order_status(
            order_id,
            StatusEnum.CANCELLED
        )

    async def cancel_paid_order(self, user_id: int, order_id: int) -> None:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to user")
        if order.status != StatusEnum.PAID:
            raise ValueError(
                "Only paid orders can be cancelled via this method"
            )
        await self._order_repository.update_order_status(
            order_id,
            StatusEnum.CANCELLED
        )

    async def confirm_order(self, user_id: int, order_id: int) -> Order:
        order = await self._order_repository.get_order_by_id(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Order not found or does not belong to user")
        if order.status != StatusEnum.PENDING:
            raise ValueError("Only pending orders can be confirmed")

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

        payment_url = trigger_payment_gateway(order_id)

        return await self._order_repository.get_order_by_id(order_id)


def trigger_payment_gateway(order_id: int) -> str:
    return f"https://fake-payment-gateway.com/pay/order/{order_id}"
