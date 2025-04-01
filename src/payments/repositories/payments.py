from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Sequence

from src.database.models.orders import OrderModel, StatusEnum, OrderItemModel
from src.database.models.payments import (
    PaymentModel, PaymentStatus, PaymentItemModel
)


async def repo_get_payment_history(
        db: AsyncSession, user_id: int
) -> Sequence[PaymentModel]:
    payment_history_res = await db.execute(select(
        PaymentModel).filter_by(user_id=user_id))
    return payment_history_res.scalars().all()


async def repo_get_payment_history_admin(
        db: AsyncSession,
        user_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> Sequence[PaymentModel]:
    payment_history_query = select(PaymentModel)

    if user_id:
        payment_history_query = payment_history_query.filter_by(user_id=user_id)

    if status:
        payment_history_query = payment_history_query.filter_by(status=status)

    if start_date:
        payment_history_query = payment_history_query.filter(
            PaymentModel.created_at >= start_date)

    if end_date:
        payment_history_query = payment_history_query.filter(
            PaymentModel.created_at <= end_date)

    result = await db.execute(payment_history_query)
    return result.scalars().all()


async def repo_create_payment_record(
        db: AsyncSession, payment_data: dict
) -> PaymentModel:
    new_payment = PaymentModel(**payment_data)
    db.add(new_payment)
    await db.flush()
    return new_payment


async def repo_get_order_by_id(
        db: AsyncSession, order_id: int
) -> Optional[OrderModel]:
    result = await db.execute(select(OrderModel).filter_by(id=order_id))
    return result.scalars().first()


async def repo_update_order_status(
        db: AsyncSession, order: OrderModel, status: StatusEnum
) -> None:
    order.status = status
    await db.commit()
    await db.refresh(order)


async def repo_create_payment_items(
        db: AsyncSession, order_items: list[OrderItemModel], payment_id: int
) -> List[PaymentItemModel]:
    payment_items = []
    for item in order_items:
        new_payment_item = PaymentItemModel(
            payment_id=payment_id,
            order_item_id=item.id,
            price_at_payment=item.price_at_order
        )
        payment_items.append(new_payment_item)
        db.add(new_payment_item)
        await db.flush()
    return payment_items
