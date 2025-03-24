import os

import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import UserModel
from src.database.models.orders import OrderModel, StatusEnum
from src.database.models.payments import PaymentModel, PaymentStatus
from src.database.session_postgresql import get_postgresql_db
from src.payments.schemas.payments import OrderSchema
from src.accounts.services.email_service import EmailService

STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")


router = APIRouter()


@router.post("/{order_id}")
async def create_payment(
        order_id:int,
        request: Request,
        db: AsyncSession = Depends(get_postgresql_db),

):
    current_order_res = await db.execute(select(OrderModel).filter_by(id=order_id))
    current_order = current_order_res.scalars().first()

    if not current_order:
        raise HTTPException(status_code=400, detail="Order not found")

    if  current_order.status != StatusEnum.PENDING:
        raise HTTPException(
            status_code=400, detail="Order is not available for payment."
        )

    unit_amount = current_order.total_amount

    if unit_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid total sum.")

    new_payment = PaymentModel(
        user_id=current_order.user_id,
        order_id=current_order.id,
        amount=current_order.total_amount,
    )

    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    user_res = await db.execute(
        select(UserModel).filter_by(id=current_order.user_id)
    )
    user = user_res.scalars().first()

    if not user or not user.email:
        raise HTTPException(status_code=400, detail="User email not found")

    # items = []
    # for item in current_order.items:
    #     items.append(
    #         {
    #             "price_data": {
    #                 "currency": "usd",
    #                 "product_data": {
    #                     "name": f"{item.movie.name} - Order #{order_id}"},
    #                 "unit_amount": int(item.price_at_order * 100)
    #             },
    #             "quantity": 1,
    #         }
    #     )



    base_url = str(request.base_url).rstrip("/")
    success_url = f"{base_url}/api/v1/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/api/v1/payments/cancel?session_id={{CHECKOUT_SESSION_ID}}"

    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Order #{order_id}"},
                    "unit_amount": int(unit_amount * 100)
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": order_id,
                "payment_id": new_payment.id,
                "user_email": user.email
            },
        )
        new_payment.external_payment_id = session.id
        await db.commit()

        return {
            "payment_url": session.url
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/success/")
async def success_payment(
        session_id: str,
        db: AsyncSession = Depends(get_postgresql_db)
) -> JSONResponse:
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata

        if not metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing metadata in Stripe session"
            )

        order_id = metadata.get("order_id")
        payment_id = metadata.get("payment_id")
        user_email = metadata.get("user_email")

        if not order_id or not payment_id or not user_email:
            raise HTTPException(
                status_code=400,
                detail="Missing order_id or payment_id in metadata"
            )

        try:
            order_id = int(order_id)
            payment_id = int(payment_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format.")

        payment_res = await db.execute(select(PaymentModel).filter_by(
            id=payment_id))
        payment = payment_res.scalars().first()

        if not payment:
            raise HTTPException(
                status_code=400,
                detail="Payment not found."
            )

        payment.status = PaymentStatus.SUCCESSFUL
        await db.flush()

        order_res = await db.execute(select(OrderModel).filter_by(id=order_id))
        order = order_res.scalars().first()

        if not order:
            raise HTTPException(
                status_code=400,
                detail="Order not found."
            )
        order.status = StatusEnum.PAID
        # await email_service.confirmation_payment_email(user_email, order_id)

        await db.commit()
        return JSONResponse(
            content={"message": "The payment has been completed successfully."}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cancel/")
async def cancel_payment(
        session_id: str,
        db: AsyncSession = Depends(get_postgresql_db)
) -> JSONResponse:
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata

        if not metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing metadata in Stripe session"
            )

        order_id = metadata.get("order_id")
        payment_id = metadata.get("payment_id")
        user_email = metadata.get("user_email")

        if not order_id or not payment_id or not user_email:
            raise HTTPException(
                status_code=400,
                detail="Missing order_id or payment_id in metadata"
            )

        try:
            order_id = int(order_id)
            payment_id = int(payment_id)

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format.")

        payment_res = await db.execute(select(PaymentModel).filter_by(
            id=payment_id))
        payment = payment_res.scalars().first()

        if not payment:
            raise HTTPException(
                status_code=400,
                detail="Payment not found."
            )

        payment.status = PaymentStatus.CANCELED
        await db.flush()

        order_res = await db.execute(select(OrderModel).filter_by(id=order_id))
        order = order_res.scalars().first()

        if not order:
            raise HTTPException(
                status_code=400,
                detail="Order not found."
            )
        order.status = StatusEnum.CANCELLED
        # await email_service.cancellation_payment_email(
        #     user_email, order_id
        # )

        await db.commit()
        return JSONResponse(
            content={"message": "The payment was canceled."}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_payments_list():
    return {"message": "Payments endpoint works!"}


@router.get("/{payment_id}")
async def get_payment_detail():
    return {"message": "Payments endpoint works!"}


@router.get("/orders/{order_id}", response_model=OrderSchema)
async def test(order_id: int, db: AsyncSession = Depends(get_postgresql_db)) -> OrderSchema:
    order_res = await db.execute(select(OrderModel).filter_by(id=order_id))
    order = order_res.scalars().first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderSchema.model_validate(order)

