from database.models.shopping_carts import CartItemModel


def validate_movie_not_in_purchases(
        cart_item: CartItemModel,
        movie_id: int
        ) -> int:
    if cart_item.cart and cart_item.cart.user:
        user = cart_item.cart.user
        for purchase in user.purchases:
            if purchase.movie_id == movie_id:
                raise ValueError(
                    f"Movie with id {movie_id} has already been purchased"
                    )
    return movie_id


def validate_movie_not_in_cart(cart_item: CartItemModel, movie_id: int) -> int:
    if cart_item.cart:
        for item in cart_item.cart.items:
            if item.movie_id == movie_id and item is not cart_item:
                raise ValueError(
                    f"Movie with id {movie_id} is already in the cart"
                    )
    return movie_id
