from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from src.database.models import StatusEnum


class OrderItemResponseSchema(BaseModel):
    id: int
    movie_id: int
    price_at_order: float
    name: str
    genres: Optional[List[str]] = None
    year: int

    model_config = {"from_attributes": True}


class OrderResponseSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: StatusEnum
    total_amount: float | None
    items: List[OrderItemResponseSchema]

    model_config = {"from_attributes": True}


class OrderListResponseSchema(BaseModel):
    orders: List[OrderResponseSchema]
    total: int


class OrderFilterSchema(BaseModel):
    user_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[StatusEnum] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class OrderStatusUpdateSchema(BaseModel):
    status: StatusEnum


class MessageResponseSchema(BaseModel):
    message: str
