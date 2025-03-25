from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from database.models import StatusEnum


@dataclass
class OrderItem:
    id: int
    order_id: int
    movie_id: int
    price_at_order: float
    name: str
    year: int
    genres: Optional[List[str]] = None


@dataclass
class Order:
    id: int
    user_id: int
    created_at: datetime
    status: StatusEnum
    items: List[OrderItem]
    total_amount: Optional[List[str]] = None
