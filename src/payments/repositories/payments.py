from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from src.database.models.payments import PaymentModel


async def repo_get_payment_history(db: AsyncSession, user_id: int) -> List[
    PaymentModel]:
    payment_history_res = await db.execute(select(PaymentModel).filter_by(user_id=user_id))
    return payment_history_res.scalars().all()
