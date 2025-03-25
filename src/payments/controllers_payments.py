# async def get_user_payments(
#         user: UserModel = Depends(get_current_user),
#         order_service: OrderServiceInterface = Depends(get_order_service),
# ) -> OrderListResponseSchema:
#     # Retrieve a list of all orders for the user.
#     # Args:
#     #     user (UserModel): Current authenticated user.
#     #     order_service (OrderServiceInterface): Order service instance.
#     # Returns:
#     #     OrderListResponseSchema: List of user's orders.
#     orders = await order_service.get_user_orders(user.id)
#     return OrderListResponseSchema(orders=orders)