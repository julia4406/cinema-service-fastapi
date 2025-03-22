#
#
#
# def validate_movie_not_in_orders(
#         cart_item: CartItemModel,
#         movie_id: int
# ) -> int:
#     from database.models.shopping_carts import CartItemModel
#     if cart_item.cart and cart_item.cart.user:
#         user = cart_item.cart.user
#         for order in user.orders:
#             for item in order.items:
#                 if item.movie_id == movie_id:
#                     raise ValueError(
#                         f"Movie with id {movie_id} is already in user's orders"
#                     )
#     return movie_id
#
#
# def validate_movie_not_in_cart(cart_item: CartItemModel, movie_id: int) -> int:
#     from database.models.shopping_carts import CartItemModel
#     if cart_item.cart:
#         for item in cart_item.cart.items:
#             if item.movie_id == movie_id and item is not cart_item:
#                 raise ValueError(
#                     f"Movie with id {movie_id} is already in the cart"
#                 )
#     return movie_id
