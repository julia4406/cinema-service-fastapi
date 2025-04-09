from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.logging_settings import logger
from src.database.models.orders import OrderItemModel, OrderModel, StatusEnum
from src.database.models.payments import PaymentItemModel, PaymentModel, PaymentStatus


async def get_payment_history_by_user_id(
        db: AsyncSession, user_id: int
) -> Sequence[PaymentModel]:
    logger.info(f"Fetching payment history for user_id={user_id}")
    payment_history_res = await db.execute(
        select(PaymentModel).filter_by(user_id=user_id))
    payments = payment_history_res.scalars().all()

    if not payments:
        logger.warning(f"No payment history found for user_id={user_id}")

    return payments


async def get_payment_history_as_admin(
        db: AsyncSession,
        user_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> Sequence[PaymentModel]:
    logger.info(f"Fetching admin payment history with filters: "
                f"user_id={user_id}, status={status}, start_date={start_date}, end_date={end_date}")

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
    payments = result.scalars().all()

    if not payments:
        logger.warning("No payment records found with the given filters.")

    return payments


async def create_payment_record(
        db: AsyncSession, payment_data: dict
) -> PaymentModel:
    logger.info("Creating a new payment record.")
    new_payment = PaymentModel(**payment_data)
    db.add(new_payment)

    try:
        await db.flush()
        logger.info(f"Payment record created successfully (id={new_payment.id}).")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create payment record: {e}")
        raise

    return new_payment


async def get_order_by_id(
        db: AsyncSession, order_id: int
) -> Optional[OrderModel]:
    logger.info(f"Fetching order by id={order_id}")
    result = await db.execute(select(OrderModel).filter_by(id=order_id))
    order = result.scalars().first()

    if not order:
        logger.warning(f"Order not found (id={order_id})")

    return order


async def update_order_status(
        db: AsyncSession, order: OrderModel, status: StatusEnum
) -> None:
    logger.info(f"Updating order status (id={order.id}) to {status}")
    order.status = status

    try:
        await db.commit()
        await db.refresh(order)
        logger.info(
            f"Order status updated successfully (id={order.id}, new_status={status})"
        )
    except SQLAlchemyError as e:
        logger.error(f"Failed to update order status (id={order.id}): {e}")
        raise


async def create_payment_items(
        db: AsyncSession, order_items: list[OrderItemModel], payment_id: int
) -> List[PaymentItemModel]:
    logger.info(f"Creating payment items for payment_id={payment_id}")
    payment_items = []

    try:
        for item in order_items:
            new_payment_item = PaymentItemModel(
                payment_id=payment_id,
                order_item_id=item.id,
                price_at_payment=item.price_at_order
            )
            payment_items.append(new_payment_item)
            db.add(new_payment_item)
            await db.flush()

        logger.info(
            f"Created {len(payment_items)} payment items for payment_id={payment_id}"
        )
    except SQLAlchemyError as e:
        logger.error(
            f"Failed to create payment items for payment_id={payment_id}: {e}"
        )
        raise

    return payment_items
