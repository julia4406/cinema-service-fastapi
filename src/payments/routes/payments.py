import os

import stripe
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.repositories.payments import PaymentRepository
from src.payments.services.payments import get_metadata
from src.payments.validators.payments_validators import validate_email
from src.database.models import UserModel
from src.database.models.orders import OrderModel, StatusEnum
from src.database.models.payments import PaymentModel, PaymentStatus
from src.database.session_postgresql import get_postgresql_db
from src.accounts.services.email_service import EmailService, get_email_service

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
        status=PaymentStatus.PENDING
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


# @router.post("/webhook")
# async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_postgresql_db)):
#     payload = await request.body()
#     signature_header = request.headers.get("Stripe-Signature")
#     event = None
#
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, signature_header, STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         # Invalid payload
#         return JSONResponse(status_code=400,
#                             content={"message": "Invalid payload"})
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return JSONResponse(status_code=400,
#                             content={"message": "Invalid signature"})
#
#     # Обробка події "checkout.session.completed"
#     if event["type"] == "checkout.session.completed":
#         session = event["data"]["object"]
#         payment_intent = session.get("payment_intent")
#         if payment_intent:
#             # Завершення платежу, оновити статус у базі даних
#             payment = await db.execute(
#                 select(PaymentModel).filter_by(external_payment_id=session["id"]))
#             payment_record = payment.scalars().first()
#             if payment_record:
#                 payment_record.status = "success"
#                 await db.commit()
#
#         # Платіж завершено, можна виконати інші дії, наприклад, підтвердити замовлення
#         print(f"Payment successful for session {session['id']}")
#
#     # Обробка інших подій, якщо потрібно
#     # Наприклад, для скасування платежу:
#     elif event["type"] == "checkout.session.async_payment_failed":
#         session = event["data"]["object"]
#         # Встановіть статус як failed
#         payment = await db.execute(
#             select(PaymentModel).filter_by(external_payment_id=session["id"]))
#         payment_record = payment.scalars().first()
#         if payment_record:
#             payment_record.status = "failed"
#             await db.commit()
#
#     return JSONResponse(status_code=200, content={"message": "Event received"})


@router.get("/success/")
async def success_payment(
        session_id: str,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_postgresql_db),
        email_service: EmailService = Depends(get_email_service)
) -> JSONResponse:
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = get_metadata(session)

        payment_repository = PaymentRepository(db)
        await payment_repository.successful_payment_model(
            metadata.payment_id, metadata.order_id
        )

        background_tasks.add_task(
            email_service.cancellation_payment_email,
            recipient_email=metadata.user_email,
            order_id=metadata.order_id
        )

        return JSONResponse(
            content={"message": "The payment has been completed successfully."}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cancel/")
async def cancel_payment(
        session_id: str,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_postgresql_db),
        email_service: EmailService = Depends(get_email_service)
) -> JSONResponse:
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = get_metadata(session)

        payment_repository = PaymentRepository(db)
        await payment_repository.canceled_payment_model(
            metadata.payment_id, metadata.order_id
        )

        background_tasks.add_task(
            email_service.cancellation_payment_email,
            recipient_email=metadata.user_email,
            order_id=metadata.order_id
        )

        return JSONResponse(
            content={"message": "The payment was canceled."}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_payments_history():
    return {"message": "Payments endpoint works!"}


@router.get("/{payment_id}")
async def get_payment_detail():
    return {"message": "Payments endpoint works!"}


