from fastapi import APIRouter, status

from orders.controllers import admin_get_all_orders, admin_update_order_status

router = APIRouter()

router.get("/", status_code=status.HTTP_200_OK)(admin_get_all_orders)
router.patch("/{order_id}/status", status_code=status.HTTP_200_OK)(
    admin_update_order_status
)
