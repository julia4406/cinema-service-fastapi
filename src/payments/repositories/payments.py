# from fastapi import Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
#
# from src.database.models.orders import OrderModel, StatusEnum
# from src.database.models import PaymentModel, PaymentStatus
# from src.config.settings import Settings
#
#
# settings = Settings()
#
#
# class PaymentRepository:
#     def __init__(self, db: AsyncSession):
#         self.db = db
#
#     async def canceled_payment_model(
#             self, payment_id: int, order_id:int
#     ) -> None:
#         payment_res = await self.db.execute(
#             select(PaymentModel).filter_by(id=payment_id))
#         payment = payment_res.scalars().first()
#
#         if not payment:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Payment not found."
#             )
#
#         payment.status = PaymentStatus.CANCELED
#         await self.db.flush()
#
#         order_res = await self.db.execute(select(OrderModel).filter_by(
#             id=order_id
#         ))
#         order = order_res.scalars().first()
#
#         if not order:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Order not found."
#             )
#         order.status = StatusEnum.CANCELLED
#         await self.db.commit()
#
#     async def successful_payment_model(
#             self, payment_id: int, order_id:int
#     ) -> None:
#         payment_res = await self.db.execute(
#             select(PaymentModel).filter_by(id=payment_id))
#         payment = payment_res.scalars().first()
#
#         if not payment:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Payment not found."
#             )
#
#         payment.status = PaymentStatus.SUCCESSFUL
#         await self.db.flush()
#
#         order_res = await self.db.execute(select(OrderModel).filter_by(
#             id=order_id
#         ))
#         order = order_res.scalars().first()
#
#         if not order:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Order not found."
#             )
#         order.status = StatusEnum.PAID
#         await self.db.commit()
#
#
