from datetime import datetime

from pydantic import BaseModel
from src.database.models.orders import StatusEnum


class PaymentCreateSchema(BaseModel):
    ...

class OrderSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: StatusEnum
    total_amount: float | None

    model_config = {
        "from_attributes": True
    }
