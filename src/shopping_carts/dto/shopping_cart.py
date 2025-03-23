from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class CartItem:
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime


@dataclass
class ShoppingCart:
    id: int
    user_id: int
    items: List[CartItem]


@dataclass
class Purchase:
    id: int
    user_id: int
    movie_id: int
    purchased_at: datetime
