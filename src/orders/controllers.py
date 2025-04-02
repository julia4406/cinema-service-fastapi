from fastapi import Depends, HTTPException, status

from src.database.models import UserGroupEnum
from src.database.models import UserModel
from src.accounts.dependencies import get_current_user, role_required

from src.database.exceptions.orders import CreateOrderError, OrderUpdateError
from src.orders.dependencies import get_order_service, get_admin_order_service
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
    except OrderUpdateError as e:
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
    total = len(orders)
    return OrderListResponseSchema(orders=orders, total=total)


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
    except OrderUpdateError as e:
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
    except OrderUpdateError as e:
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
    except OrderUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_get_all_orders(
        filters: OrderFilterSchema = Depends(),
        order_service: get_admin_order_service = Depends(get_order_service),
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN))
):
    """Retrieve a list of all orders with filters and pagination for admins.
        Args:
            filters (OrderFilterSchema): Filtering options including user_id, date range, status, limit, and offset.
            order_service (OrderServiceInterface): Order service instance.
            admin (UserModel): Current authenticated admin user.
        Returns:
            OrderListResponseSchema: List of orders with total count.
        """
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
    except OrderUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_update_order_status(
        order_id: int,
        update_data: OrderStatusUpdateSchema,
        order_service: get_admin_order_service = Depends(get_order_service),
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN))
):
    """Update the status of a specific order manually by an admin.
        Args:
            order_id (int): ID of the order to update.
            update_data (OrderStatusUpdateSchema): New status data for the order.
            order_service (OrderServiceInterface): Order service instance.
            admin (UserModel): Current authenticated admin user.
        Returns:
            OrderResponseSchema: Updated order details.
        """
    try:
        order = await order_service.update_order_status(
            order_id,
            update_data.status
        )
        return OrderResponseSchema(**order.__dict__)
    except OrderUpdateError as e:
        raise HTTPException(status_code=404, detail=str(e))
