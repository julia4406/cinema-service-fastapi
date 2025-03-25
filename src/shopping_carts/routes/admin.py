from fastapi import APIRouter, status

from src.shopping_carts.controllers import (
    admin_get_user_cart,
    admin_add_movie_to_cart,
    admin_remove_movie_from_cart,
    admin_clear_user_cart
)

router = APIRouter()

router.get("/{user_id}/cart", status_code=status.HTTP_200_OK)(
    admin_get_user_cart
    )
router.post("/{user_id}/cart/items", status_code=status.HTTP_200_OK)(
    admin_add_movie_to_cart
    )
router.delete(
    "/{user_id}/cart/items/{movie_id}",
    status_code=status.HTTP_200_OK
    )(admin_remove_movie_from_cart)
router.delete("/{user_id}/cart", status_code=status.HTTP_200_OK)(
    admin_clear_user_cart
    )
