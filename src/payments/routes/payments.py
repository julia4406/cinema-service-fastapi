import os

import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.orders import OrderModel, StatusEnum
from src.database.models.payments import PaymentModel, PaymentStatus
from src.database.session_postgresql import get_postgresql_db
from payments.schemas.payments import OrderSchema

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
    cancel_url = f"{base_url}/api/v1/payments/cancel"

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items={
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Order #{order_id}"},
                    "unit_amount": int(unit_amount * 100)
                },
                "quantity": 1,
            },
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"order_id": order_id, "payment_id": new_payment.id},
        )
        new_payment.external_payment_id = session.id
        await db.commit()

        return {"payment_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/success/")
async def success_payment(
        session_id: str,
        db: AsyncSession = Depends(get_postgresql_db)
) -> JSONResponse:
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_status = session.payment_status
        metadata = session.metadata

        if not metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing metadata in Stripe session"
            )

        order_id = metadata.get("order_id")
        payment_id = metadata.get("payment_id")

        if not order_id or not payment_id:
            raise HTTPException(
                status_code=400,
                detail="Missing order_id or payment_id in metadata"
            )

        payment_res = await db.execute(select(PaymentModel).filter_by(
            id=payment_id))
        payment = payment_res.scalars().first()

        if not payment:
            raise HTTPException(
                status_code=400,
                detail="Payment not found."
            )

        if payment_status == "paid":
            payment.status = PaymentStatus.SUCCESSFUL
        elif payment_status == "canceled":
            payment.status = PaymentStatus.CANCELED
        else:
            payment.status = PaymentStatus.REFUNDED

        await db.flush()

        order_res = await db.execute(select(OrderModel).filter_by(id=order_id))
        order = order_res.scalars().first()

        if not order:
            raise HTTPException(
                status_code=400,
                detail="Order not found."
            )
        if payment.status == PaymentStatus.SUCCESSFUL:
            order.status = StatusEnum.PAID

        await db.commit()
        return JSONResponse(
            content={"message": "The payment has been completed successfully."}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cancel/")
async def cancel_payment() -> JSONResponse:
    # Тут ти можеш виконати додаткові дії, наприклад, перевірити статус сесії через Stripe API
    # або оновити статус замовлення в базі даних
    return JSONResponse(
        content={"message": "The payment was canceled."}
    )


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

