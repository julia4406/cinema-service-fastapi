from database.models.purchased import PurchasedModel


def validate_movie_not_already_purchased(
        purchase: PurchasedModel,
        movie_id: int
) -> int:
    if purchase.user:
        for existing_purchase in purchase.user.purchases:
            if existing_purchase.movie_id == movie_id and existing_purchase is not purchase:
                raise ValueError(
                    f"Movie with id {movie_id} is already purchased by user {purchase.user_id}"
                )
    return movie_id
