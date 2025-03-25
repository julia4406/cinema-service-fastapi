from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, DateTime, DECIMAL, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum

from src.database.models import Base


class PaymentStatus(Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"
    PENDING = "pending"


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLAlchemyEnum(PaymentStatus),
        default=PaymentStatus.SUCCESSFUL,
    )
    amount: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        nullable=False
    )
    external_payment_id: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    payment_items: Mapped[list["PaymentItemModel"]] = relationship(
        "PaymentItemModel",
        back_populates="payment"
    )


class PaymentItemModel(Base):
    __tablename__ = "payment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    price_at_payment: Mapped[float] = mapped_column(
        DECIMAL(10, 2), nullable=False
    )

    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel",
        back_populates="payment_items"
    )
    order_item: Mapped["OrderItemModel"] = relationship(
        "OrderItemModel",
        back_populates="payment_items"
    )
