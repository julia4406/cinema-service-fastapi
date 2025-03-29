import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, \
    Query
from fastapi.responses import JSONResponse

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.payments.schemas.payments import (
    CreatePaymentSchema, EmailSchema, PaymentHistorySchema, PaymentResponseSchema
)
from src.database.models import UserModel
from src.database.models.payments import (
    PaymentModel, PaymentStatus, PaymentItemModel
)
from src.database.models.orders import OrderModel, StatusEnum, OrderItemModel
from src.database.session_postgresql import get_postgresql_db
from src.database.models.accounts import UserGroupEnum
from src.accounts.services.email_service import EmailService, get_email_service
from src.accounts.dependencies import role_required

STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        email_service: EmailService = Depends(get_email_service),
        db: AsyncSession = Depends(get_postgresql_db)
):
    stripe_signature = request.headers.get("stripe-signature")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="No stripe signature")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as e:
        return JSONResponse(
            {"status": "error", "message": f"Invalid payload: {str(e)}"},
            status_code=400
        )
    except stripe.error.SignatureVerificationError:
        return JSONResponse({"status": "error", "message": "Invalid signature"},
                            status_code=400)

    if event.type == "checkout.session.completed":
        session = event.data.object

        payment_data = CreatePaymentSchema(
            user_id=int(session["metadata"]["user_id"]),
            order_id=int(session["metadata"]["order_id"]),
            status=PaymentStatus.SUCCESSFUL,
            amount=Decimal(session["metadata"]["total_amount"]),
            external_payment_id=session["payment_intent"]
        )
        new_payment = PaymentModel(**payment_data.model_dump())

        db.add(new_payment)
        await db.flush()

        order_res = await db.execute(
            select(OrderModel)
            .options(joinedload(OrderModel.items))
            .filter_by(id=int(session["metadata"]["order_id"]))
        )
        order = order_res.scalars().first()

        if order:
            order.status = StatusEnum.PAID

            payment_items = []
            for item in order.items:
                new_payment_item = PaymentItemModel(
                    payment_id=new_payment.id,
                    order_item_id=item.id,
                    price_at_payment=item.price_at_order
                )
                payment_items.append(new_payment_item)
                db.add(new_payment_item)
                await db.flush()

            await db.commit()
            await db.refresh(order)
            await db.refresh(new_payment)

        user_email = EmailSchema(email=session["metadata"]["user_email"]).email
        background_tasks.add_task(
            email_service.confirmation_payment_email,
            recipient_email=user_email,
            order_id=session["metadata"]["order_id"]
        )

        return JSONResponse(
            {"status": "success", "message": "Payment created"},
            status_code=201
        )

    elif event.type in ["checkout.session.async_payment_failed", "checkout.session.payment_failed"]:
        session = event.data.object

        payment_data = CreatePaymentSchema(
            user_id=int(session["metadata"]["user_id"]),
            order_id=int(session["metadata"]["order_id"]),
            status=PaymentStatus.CANCELED,
            amount=Decimal(session["metadata"]["total_amount"]),
            external_payment_id=session["payment_intent"]
        )
        new_payment = PaymentModel(**payment_data.model_dump())

        db.add(new_payment)
        await db.commit()
        await db.refresh(new_payment)

        user_email = EmailSchema(email=session["metadata"]["user_email"]).email
        background_tasks.add_task(
            email_service.cancellation_payment_email,
            recipient_email=user_email,
            order_id=session["metadata"]["order_id"]
        )

        return JSONResponse(
            {"status": "cancel", "message": "Payment cancelled"},
            status_code=400
        )


@router.post("/{order_id}")
async def create_payment(
        order_id: int,
        request: Request,
        current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
        db: AsyncSession = Depends(get_postgresql_db),
):
    current_order_res = await db.execute(
        select(OrderModel)
        .options(
            selectinload(OrderModel.items)
            .selectinload(OrderItemModel.movie)
        )
        .filter_by(id=order_id)
    )

    current_order = current_order_res.scalars().first()

    if not current_order:
        raise HTTPException(status_code=400, detail="Order not found")

    if current_order.status != StatusEnum.PENDING:
        raise HTTPException(
            status_code=400, detail="Order is not available for payment."
        )

    unit_amount = current_order.total_amount

    if unit_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid total sum.")

    user_res = await db.execute(
        select(UserModel).filter_by(id=current_order.user_id)
    )
    user = user_res.scalars().first()

    if not user or not user.email:
        raise HTTPException(status_code=400, detail="User email not found")

    if unit_amount != sum(item.price_at_order for item in current_order.items):
        raise HTTPException(status_code=400, detail="Not valid total summ.")

    base_url = str(request.base_url).rstrip("/")
    success_url = f"{base_url}/api/v1/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/api/v1/payments/cancel"

    try:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{item.movie.name} - Order #{order_id}"},
                        "unit_amount": int(item.price_at_order * 100)
                    },
                    "quantity": 1,
                } for item in current_order.items
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": order_id,
                "user_id": user.id,
                "user_email": user.email,
                "total_amount": unit_amount
            },
        )

        return {
            "payment_url": session.url
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/success/")
async def success_payment() -> JSONResponse:
    return JSONResponse(
        content={"message": "The payment has been successfully completed."}
    )


@router.get("/cancel/")
async def cancel_payment() -> JSONResponse:
    return JSONResponse(
        content={"message": "The payment has been canceled."}
    )


@router.get("/history/")
async def get_payments_history(
        current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
        db: AsyncSession = Depends(get_postgresql_db),
):
    payment_history_res = await db.execute(
        select(PaymentModel).filter_by(user_id=current_user.id)
    )

    payment_history = payment_history_res.scalars().all()

    return [
        PaymentHistorySchema(
            created_at=item.created_at,
            amount=Decimal(item.amount),
            status=item.status
        ) for item in payment_history
    ]


@router.get("/history/staff/")
async def get_payments_history(
        current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
        db: AsyncSession = Depends(get_postgresql_db),
        user_id: int | None = Query(None, description="user ID for filtering."),
        status: PaymentStatus | None = Query(
            None,
            description="Filter by status successful, refunded, canceled)."),
        start_date: Optional[datetime] | None = Query(
            None, description="Start date (YYYY-MM-DD)."
        ),
        end_date: Optional[datetime] | None = Query(
            None, description="End date (YYYY-MM-DD)."
        )
):
    payment_history_query = select(PaymentModel)

    if user_id:
        payment_history_query = payment_history_query.filter_by(user_id=user_id)

    if status:
        payment_history_query = payment_history_query.filter_by(status=status)

    if start_date:
        payment_history_query = payment_history_query.filter(PaymentModel.created_at >= start_date)

    if end_date:
        payment_history_query= payment_history_query.filter(PaymentModel.created_at <= end_date)

    payment_history_res =  await db.execute(payment_history_query)
    payment_history = payment_history_res.scalars().all()

    return [
        PaymentResponseSchema(
            id=item.id,
            user_id=item.user_id,
            order_id=item.order_id,
            amount=Decimal(item.amount),
            status=item.status,
            created_at=item.created_at,
            external_payment_id=item.external_payment_id
        ) for item in payment_history
    ]
