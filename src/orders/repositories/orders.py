from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.database.exceptions.orders import CreateOrderError, OrderUpdateError
from src.database.models.orders import OrderModel, OrderItemModel, StatusEnum
from src.database.models.movies import MovieModel
from src.database.utils import object_as_dict
from src.orders.dto.orders import Order, OrderItem
from src.orders.interfaces.repositories import OrderRepositoryInterface
from src.shopping_carts.dto.shopping_cart import CartItem
from src.config.logging_settings import logger  # Importing logger


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_order(
            self,
            user_id: int,
            cart_items: List[CartItem]
    ) -> Order:
        try:
            logger.info(f"Creating order for user_id: {user_id}")

            existing_pending = await self._session.execute(
                select(OrderModel)
                .filter_by(user_id=user_id, status=StatusEnum.PENDING)
                .options(joinedload(OrderModel.items))
            )
            pending_orders = existing_pending.unique().scalars().all()
            pending_movie_ids = {
                item.movie_id for order in pending_orders for item in
                order.items
            }
            new_movie_ids = {item.movie_id for item in cart_items}
            if pending_movie_ids & new_movie_ids:
                logger.warning(f"Some movies are already in a pending order for user_id {user_id}")
                raise ValueError("Some movies are already in a pending order")

            total_amount = sum(item.price for item in cart_items)
            order = OrderModel(
                user_id=user_id,
                status=StatusEnum.PENDING,
                total_amount=total_amount
            )
            self._session.add(order)
            await self._session.flush()

            for cart_item in cart_items:
                order_item = OrderItemModel(
                    order_id=order.id,
                    movie_id=cart_item.movie_id,
                    price_at_order=cart_item.price
                )
                self._session.add(order_item)

            await self._session.flush()
            await self._session.refresh(order, attribute_names=["items"])
            result = await self._session.execute(
                select(OrderModel)
                .filter_by(id=order.id)
                .options(
                    joinedload(OrderModel.items)
                    .joinedload(OrderItemModel.movie)
                    .joinedload(MovieModel.genres)
                )
            )
            order = result.scalars().first()
            if not order:
                raise ValueError("Failed to retrieve order after creation")
            order_dict = object_as_dict(order)
            order_dict["items"] = [
                OrderItem(
                    **{
                        **object_as_dict(item),
                        "name": item.movie.name,
                        "genres": [genre.name for genre in
                                   item.movie.genres] if item.movie.genres else None,
                        "year": item.movie.year
                    }
                )
                for item in order.items
            ]
            logger.info(f"Order created successfully for user_id: {user_id}")
            return Order(**order_dict)
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error creating order for user_id {user_id}: {str(e)}")
            if isinstance(e, ValueError):
                raise CreateOrderError(f"Cannot create order: {str(e)}")
            raise CreateOrderError(f"Failed to create order: {str(e)}")

    async def get_orders_by_user_id(self, user_id: int) -> List[Order]:
        logger.info(f"Fetching orders for user_id: {user_id}")
        result = await self._session.execute(
            select(OrderModel)
            .filter_by(user_id=user_id)
            .options(
                joinedload(OrderModel.items)
                .joinedload(OrderItemModel.movie)
                .joinedload(MovieModel.genres)
            )
        )
        orders = result.unique().scalars().all()
        logger.info(f"Found {len(orders)} orders for user_id: {user_id}")
        return [
            Order(
                **{
                    **object_as_dict(order),
                    "items": [
                        OrderItem(
                            **{
                                **object_as_dict(item),
                                "name": item.movie.name,
                                "genres": [
                                    genre.name for genre in item.movie.genres
                                ] if item.movie.genres else None,
                                "year": item.movie.year
                            }
                        )
                        for item in order.items
                    ]
                }
            )
            for order in orders
        ]

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        logger.info(f"Fetching order with order_id: {order_id}")
        result = await self._session.execute(
            select(OrderModel)
            .filter_by(id=order_id)
            .options(
                joinedload(OrderModel.items)
                .joinedload(OrderItemModel.movie)
                .joinedload(MovieModel.genres)
            )
        )
        order = result.scalars().first()
        if not order:
            logger.warning(f"Order with order_id {order_id} not found")
            return None
        logger.info(f"Order with order_id {order_id} found")
        order_dict = object_as_dict(order)
        order_dict["items"] = [
            OrderItem(
                **{
                    **object_as_dict(item),
                    "name": item.movie.name,
                    "genres": [genre.name for genre in
                               item.movie.genres] if item.movie.genres else None,
                    "year": item.movie.year
                }
            )
            for item in order.items
        ]
        return Order(**order_dict)

    async def update_order_status(
            self,
            order_id: int,
            status: StatusEnum
    ) -> None:
        try:
            logger.info(f"Updating order status for order_id: {order_id} to {status}")
            result = await self._session.execute(
                select(OrderModel).filter_by(id=order_id)
            )
            order = result.scalars().first()
            if not order:
                logger.warning(f"Order with order_id {order_id} not found")
                raise ValueError("Order not found")
            order.status = status
            await self._session.flush()
            logger.info(f"Order status for order_id {order_id} updated to {status}")
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error updating order status for order_id {order_id}: {str(e)}")
            if isinstance(e, ValueError):
                raise OrderUpdateError(f"Cannot update order status: {str(e)}")
            raise OrderUpdateError(f"Failed to update order status: {str(e)}")

    async def get_all_orders(
            self,
            user_id: Optional[int] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            status: Optional[StatusEnum] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[Order], int]:
        try:
            logger.info(f"Fetching all orders with filters: user_id={user_id}, date_from={date_from}, date_to={date_to}, status={status}, limit={limit}, offset={offset}")
            query = (
                select(OrderModel)
                .options(
                    joinedload(OrderModel.items)
                    .joinedload(OrderItemModel.movie)
                    .joinedload(MovieModel.genres)
                )
            )

            if user_id:
                query = query.filter(OrderModel.user_id == user_id)
            if date_from:
                query = query.filter(OrderModel.created_at >= date_from)
            if date_to:
                query = query.filter(OrderModel.created_at <= date_to)
            if status:
                query = query.filter(OrderModel.status == status)

            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self._session.execute(count_query)
            total = total_result.scalar_one()

            query = query.limit(limit).offset(offset)
            result = await self._session.execute(query)
            orders = result.unique().scalars().all()

            logger.info(f"Fetched {len(orders)} orders, total count: {total}")
            return [
                Order(
                    **{
                        **object_as_dict(order),
                        "items": [
                            OrderItem(
                                **{
                                    **object_as_dict(item),
                                    "name": item.movie.name,
                                    "genres": (
                                        [genre.name for genre in
                                         item.movie.genres]
                                        if item.movie.genres
                                        else None
                                    ),
                                    "year": item.movie.year
                                }
                            )
                            for item in order.items
                        ]
                    }
                )
                for order in orders
            ], total
        except SQLAlchemyError as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise OrderUpdateError(f"Failed to fetch orders: {str(e)}")
