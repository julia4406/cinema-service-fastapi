import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from src.accounts.schemas import UserLoginRequestSchema
from src.database.models import PaymentStatus


class PaymentListSchema(BaseModel):
    created_at: datetime.datetime
    amount: Decimal
    status: PaymentStatus

    model_config = {"from_attributes": True}


class PaymentSchema(BaseModel):
    id: int
    user_id: int
    order_id: int
    created_at: datetime.datetime
    status: PaymentStatus
    amount: Decimal
    user: UserLoginRequestSchema
    order: "OrderSchema"
    items: list["PaymentItemSchema"]

    model_config = {"from_attributes": True}


class PaymentItemSchema(BaseModel):
    id: int
    payment_id: int
    order_item_id: int
    price_at_payment: Decimal
    payment: PaymentSchema
    order_item: "OrderItemSchema"

    model_config = {"from_attributes": True}


class StripeMetadataSchema(BaseModel):
    order_id: int
    payment_id: int
    user_email: EmailStr
