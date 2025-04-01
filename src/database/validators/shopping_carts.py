from src.config.logging_settings import logger

def validate_movie_not_in_purchases(cart_item, movie_id: int) -> int:
    logger.info(f"Validating if movie with id {movie_id} is already purchased.")
    if cart_item.cart and cart_item.cart.user:
        for purchase in cart_item.cart.user.purchases:
            if purchase.movie_id == movie_id:
                logger.warning(f"Movie with id {movie_id} has already been purchased.")
                raise ValueError(
                    f"Movie with id {movie_id} has already been purchased"
                )
    logger.info(f"Movie with id {movie_id} is not in the user's purchases.")
    return movie_id


def validate_movie_not_in_cart(cart_item, movie_id: int) -> int:
    logger.info(f"Validating if movie with id {movie_id} is already in the cart.")
    if cart_item.cart:
        for item in cart_item.cart.items:
            if item.movie_id == movie_id and item is not cart_item:
                logger.warning(f"Movie with id {movie_id} is already in the cart.")
                raise ValueError(
                    f"Movie with id {movie_id} is already in the cart"
                )
    logger.info(f"Movie with id {movie_id} is not in the cart.")
    return movie_id

