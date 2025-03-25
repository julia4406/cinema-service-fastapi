from fastapi import Depends, HTTPException, status

from database.models import UserGroupEnum
from src.database.models import UserModel
from src.accounts.dependencies import get_current_user, role_required

from src.database.exceptions.orders import CreateOrderError, OrderUpdateError
from src.orders.dependencies import get_order_service
from src.orders.interfaces.services import (
    OrderServiceInterface,
    AdminOrderServiceInterface
)
from src.orders.schemas.orders import (
    OrderResponseSchema,
    OrderListResponseSchema,
    OrderFilterSchema,
    OrderStatusUpdateSchema
)
from src.shopping_carts.schemas.shopping_cart import MessageResponseSchema


async def create_order(
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> OrderResponseSchema:
    # Create an order from the user's cart.
    # Args:
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     OrderResponseSchema: The created order.
    try:
        order = await order_service.create_order(user.id)
        return OrderResponseSchema(**order.__dict__)
    except (ValueError, CreateOrderError) as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_user_orders(
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> OrderListResponseSchema:
    # Retrieve a list of all orders for the user.
    # Args:
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     OrderListResponseSchema: List of user's orders.
    orders = await order_service.get_user_orders(user.id)
    return OrderListResponseSchema(orders=orders)


async def get_order(
        order_id: int,
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> OrderResponseSchema:
    # Retrieve details of a specific order.
    # Args:
    #     order_id (int): ID of the order to retrieve.
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     OrderResponseSchema: Order details.
    try:
        order = await order_service.get_order(user.id, order_id)
        return OrderResponseSchema(**order.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


async def cancel_pending_order(
        order_id: int,
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> MessageResponseSchema:
    # Cancel a pending order (changes status from pending to cancelled).
    # Args:
    #     order_id (int): ID of the order to cancel.
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     MessageResponseSchema: Success message.
    try:
        await order_service.cancel_pending_order(user.id, order_id)
        return MessageResponseSchema(message="Order cancelled successfully")
    except (ValueError, OrderUpdateError) as e:
        raise HTTPException(status_code=400, detail=str(e))


async def cancel_paid_order(
        order_id: int,
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> MessageResponseSchema:
    # Cancel a paid order (changes status from paid to cancelled, temporary for user).
    # Args:
    #     order_id (int): ID of the order to cancel.
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     MessageResponseSchema: Success message.
    try:
        await order_service.cancel_paid_order(user.id, order_id)
        return MessageResponseSchema(
            message="Paid order cancelled successfully"
        )
    except (ValueError, OrderUpdateError) as e:
        raise HTTPException(status_code=400, detail=str(e))


async def confirm_order(
        order_id: int,
        user: UserModel = Depends(get_current_user),
        order_service: OrderServiceInterface = Depends(get_order_service),
) -> OrderResponseSchema:
    # Confirm an order (changes status from pending to paid).
    # Args:
    #     order_id (int): ID of the order to confirm.
    #     user (UserModel): Current authenticated user.
    #     order_service (OrderServiceInterface): Order service instance.
    # Returns:
    #     OrderResponseSchema: Updated order details.
    try:
        order = await order_service.confirm_order(user.id, order_id)
        return OrderResponseSchema(**order.__dict__)
    except (ValueError, OrderUpdateError) as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_all_orders(
        filters: OrderFilterSchema = Depends(),
        order_service: OrderServiceInterface = Depends(get_order_service),
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN))
):
    try:
        orders, total = await order_service.get_all_orders(
            filters.user_id,
            filters.date_from,
            filters.date_to,
            filters.status,
            filters.limit,
            filters.offset
        )
        return OrderListResponseSchema(orders=orders, total=total)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update_order_status(
        order_id: int,
        update_data: OrderStatusUpdateSchema,
        order_service: AdminOrderServiceInterface = Depends(get_order_service),
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN))
):
    try:
        order = await order_service.update_order_status(
            order_id,
            update_data.status
        )
        return OrderResponseSchema(**order.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
