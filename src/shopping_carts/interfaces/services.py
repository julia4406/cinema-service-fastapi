from src.shopping_carts.dto.shopping_cart import ShoppingCart, CartItem


class CartServiceInterface:
    async def get_cart(self, user_id: int) -> ShoppingCart:
        pass

    async def create_cart(self, user_id: int) -> ShoppingCart:
        pass

    async def add_item_to_cart(self, user_id: int, movie_id: int) -> CartItem:
        pass

    async def remove_item_from_cart(self, item_id: int) -> None:
        pass

    async def clear_cart(self, user_id: int) -> None:
        pass


class AdminCartServiceInterface:
    async def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        pass

    async def add_item_to_cart(
            self,
            user_id: int,
            movie_id: int
            ) -> ShoppingCart:
        pass

    async def remove_item_from_cart(
            self,
            user_id: int,
            movie_id: int
            ) -> ShoppingCart:
        pass

    async def clear_cart(self, user_id: int) -> ShoppingCart:
        pass
