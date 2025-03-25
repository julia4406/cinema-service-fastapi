from fastapi import Depends, HTTPException

from src.database.models import UserGroupEnum
from src.accounts.dependencies import get_current_user, role_required
from src.database.exceptions.shopping_cart import (
    CreateCartError,
    CartItemError
)
from src.database.models import UserModel
from src.shopping_carts.dependencies import (
    get_cart_service,
    get_admin_cart_service
)
from src.shopping_carts.interfaces.services import (
    CartServiceInterface,
    AdminCartServiceInterface
)
from src.shopping_carts.schemas.shopping_cart import (
    CartResponseSchema,
    CartItemResponseSchema,
    MessageResponseSchema
)


async def get_cart(
        user: UserModel = Depends(get_current_user),
        cart_service: CartServiceInterface = Depends(get_cart_service),
) -> CartResponseSchema:
    """
    Retrieve the user's cart.
    Args:
        user (UserModel): The current user object.
        cart_service (CartServiceInterface): Cart domain logic.
    Returns:
        CartResponseSchema: The user's cart.
    """
    cart = await cart_service.get_cart(user.id)
    return CartResponseSchema(**cart.__dict__)


async def create_cart(
        user: UserModel = Depends(get_current_user),
        cart_service: CartServiceInterface = Depends(get_cart_service),
) -> CartResponseSchema:
    """
    Create a new cart for the user.
    Args:
        user (UserModel): The current user object.
        cart_service (CartServiceInterface): Cart domain logic.
    Returns:
        CartResponseSchema: The created cart.
    """
    try:
        cart = await cart_service.create_cart(user.id)
        return CartResponseSchema(**cart.__dict__)
    except CreateCartError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def add_item_to_cart(
        movie_id: int,
        user: UserModel = Depends(get_current_user),
        cart_service: CartServiceInterface = Depends(get_cart_service),
) -> CartItemResponseSchema:
    """
    Add an item to the user's cart.
    Args:
        movie_id (int): The ID of the movie to add.
        user (UserModel): The current user object.
        cart_service (CartServiceInterface): Cart domain logic.
    Returns:
        CartItemResponseSchema: The added cart item.
    """
    try:
        item = await cart_service.add_item_to_cart(user.id, movie_id)
        return CartItemResponseSchema(**item.__dict__)
    except CartItemError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def remove_item_from_cart(
        item_id: int,
        cart_service: CartServiceInterface = Depends(get_cart_service),
) -> MessageResponseSchema:
    """
    Remove an item from the user's cart.
    Args:
        item_id (int): The ID of the cart item to remove.
        cart_service (CartServiceInterface): Cart domain logic.
    Returns:
        MessageResponseSchema: Success message.
    """
    try:
        await cart_service.remove_item_from_cart(item_id)
        return MessageResponseSchema(message="Item removed successfully")
    except CartItemError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def clear_cart(
        user: UserModel = Depends(get_current_user),
        cart_service: CartServiceInterface = Depends(get_cart_service),
) -> MessageResponseSchema:
    """
    Clear all items from the user's cart.
    Args:
        user (UserModel): The current user object.
        cart_service (CartServiceInterface): Cart domain logic.
    Returns:
        MessageResponseSchema: Success message.
    """
    try:
        await cart_service.clear_cart(user.id)
        return MessageResponseSchema(message="Cart cleared successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CartItemError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_get_user_cart(
        user_id: int,
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
        cart_service: AdminCartServiceInterface = Depends(
            get_admin_cart_service
            ),
) -> CartResponseSchema:
    cart = await cart_service.get_or_create_cart(user_id)
    return CartResponseSchema(**cart.__dict__)


async def admin_add_movie_to_cart(
        user_id: int,
        movie_id: int,
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
        cart_service: AdminCartServiceInterface = Depends(
            get_admin_cart_service
            ),
) -> CartResponseSchema:
    try:
        cart = await cart_service.add_item_to_cart(user_id, movie_id)
        return CartResponseSchema(**cart.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_remove_movie_from_cart(
        user_id: int,
        movie_id: int,
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
        cart_service: AdminCartServiceInterface = Depends(
            get_admin_cart_service
            ),
) -> MessageResponseSchema:
    await cart_service.remove_item_from_cart(user_id, movie_id)
    return MessageResponseSchema(message="Item removed successfully")


async def admin_clear_user_cart(
        user_id: int,
        admin: UserModel = Depends(role_required(UserGroupEnum.ADMIN)),
        cart_service: AdminCartServiceInterface = Depends(
            get_admin_cart_service
            ),
) -> MessageResponseSchema:
    await cart_service.clear_cart(user_id)
    return MessageResponseSchema(message="Cart cleared successfully")
