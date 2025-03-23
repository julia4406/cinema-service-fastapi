from datetime import datetime

from pydantic import BaseModel
from database.models.orders import StatusEnum


class PaymentCreateSchema(BaseModel):
    ...

class OrderSchema(BaseModel):
    user_id: int
    created_at: datetime
    status: StatusEnum
    total_amount: float
