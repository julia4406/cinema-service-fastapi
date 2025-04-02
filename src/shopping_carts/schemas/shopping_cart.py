from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CartItemResponseSchema(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime
    name: str
    price: float
    genres: Optional[List[str]] = None
    year: int

    model_config = {
        "from_attributes": True
    }


class CartResponseSchema(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponseSchema]

    model_config = {
        "from_attributes": True
    }


class MessageResponseSchema(BaseModel):
    message: str
