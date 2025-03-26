from fastapi import APIRouter, status

from src.orders.controllers import (
    create_order,
    get_user_orders,
    get_order,
    cancel_pending_order,
    confirm_order
)

router = APIRouter(prefix="/orders", tags=["orders"])

# Create a new order from the user's cart
router.post("/", status_code=status.HTTP_201_CREATED)(create_order)

# Get a list of all user orders
router.get("/", status_code=status.HTTP_200_OK)(get_user_orders)

# Get details of a specific order
router.get("/{order_id}", status_code=status.HTTP_200_OK)(get_order)

# Cancel a pending order
router.patch("/{order_id}/cancel", status_code=status.HTTP_200_OK)(
    cancel_pending_order
)

# Confirm an order and initiate payment
router.post("/{order_id}/confirm", status_code=status.HTTP_200_OK)(
    confirm_order
)
