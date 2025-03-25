from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from database.models import StatusEnum


class OrderItemResponseSchema(BaseModel):
    id: int
    movie_id: int
    price_at_order: float
    name: str
    genres: Optional[List[str]] = None
    year: int

    class Config:
        from_attributes = True


class OrderResponseSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: StatusEnum
    total_amount: float | None
    items: List[OrderItemResponseSchema]

    class Config:
        from_attributes = True


class OrderListResponseSchema(BaseModel):
    orders: List[OrderResponseSchema]


class MessageResponseSchema(BaseModel):
    message: str
