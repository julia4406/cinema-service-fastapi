from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from src.payments.schemas.payments import PaymentHistorySchema

from src.payments.repositories.payments import repo_get_payment_history


async def service_get_payment_history(db: AsyncSession, user_id: int) -> List[
    PaymentHistorySchema]:
    payments = await repo_get_payment_history(db, user_id)
    return [
        PaymentHistorySchema(
            created_at=item.created_at,
            amount=Decimal(item.amount),
            status=item.status
        ) for item in payments
    ]
