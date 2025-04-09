from src.config.logging_settings import logger
from src.database.models.shopping_carts import PurchasedModel


def validate_movie_not_already_purchased(purchase: PurchasedModel, movie_id: int) -> int:
    logger.info(f"Validating if movie with id {movie_id} is already purchased by user {purchase.user_id}.")
    if purchase.user:
        for existing_purchase in purchase.user.purchases:
            if existing_purchase.movie_id == movie_id and existing_purchase is not purchase:
                logger.warning(f"Movie with id {movie_id} is already purchased by user {purchase.user_id}.")
                raise ValueError(
                    f"Movie with id {movie_id} is already purchased by user {purchase.user_id}"
                )
    logger.info(f"Movie with id {movie_id} has not been purchased by user {purchase.user_id}.")
    return movie_id
