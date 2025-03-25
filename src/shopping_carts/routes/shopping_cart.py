from fastapi import APIRouter, status

from src.shopping_carts.controllers import (
    get_cart,
    create_cart,
    add_item_to_cart,
    remove_item_from_cart,
    clear_cart
)

router = APIRouter()

router.get("/", status_code=status.HTTP_200_OK)(get_cart)
router.post("/", status_code=status.HTTP_201_CREATED)(create_cart)
router.post("/items/", status_code=status.HTTP_201_CREATED)(add_item_to_cart)
router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)(
    remove_item_from_cart
)
router.delete("/clear/", status_code=status.HTTP_200_OK)(clear_cart)
