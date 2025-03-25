from decimal import Decimal

from pydantic import BaseModel, EmailStr

from src.database.models.orders import OrderModel

from src.database.models import UserModel

from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from src.database.models.payments import PaymentStatus


class CreatePaymentSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    order_id: int = Field(..., gt=0)
    status: PaymentStatus
    amount: Decimal = Field(..., gt=0)
    external_payment_id: str

    model_config = {"from_attributes": True}


class PaymentResponseSchema(BaseModel):
    id: int
    user_id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    created_at: datetime
    external_payment_id: str

    class Config:
        from_attributes = True


class PaymentListSchema(BaseModel):
    created_at: datetime
    amount: Decimal
    status: PaymentStatus

    model_config = {"from_attributes": True}


class PaymentSchema(BaseModel):
    id: int
    user_id: int
    order_id: int
    created_at: datetime
    status: PaymentStatus
    amount: Decimal
    items: list["PaymentItemSchema"]

    model_config = {"from_attributes": True}


class PaymentItemSchema(BaseModel):
    id: int
    payment_id: int
    order_item_id: int
    price_at_payment: Decimal
    payment: PaymentSchema

    model_config = {"from_attributes": True}


class StripeMetadataSchema(BaseModel):
    order_id: int
    payment_id: int
    user_email: EmailStr
