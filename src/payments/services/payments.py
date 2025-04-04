from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
import stripe
from fastapi import HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import Settings
from src.email.email_service import EmailService
from stripe import Event

from src.database.models.accounts import UserModel
from src.database.models.orders import OrderModel, StatusEnum
from src.database.models.payments import PaymentStatus
from src.payments.schemas.payments import (
    PaymentHistorySchema,
    PaymentResponseSchema, CreatePaymentSchema
)
from src.payments.repositories.payments import (
    repo_get_payment_history,
    repo_get_payment_history_admin, repo_create_payment_record,
    repo_get_order_by_id, repo_update_order_status, repo_create_payment_items
)
from src.config.logging_settings import logger


settings = Settings()


async def service_get_payment_history(
        db: AsyncSession, user_id: int
) -> List[PaymentHistorySchema]:
    logger.info(f"Fetching payment history for user_id: {user_id}")
    payments = await repo_get_payment_history(db, user_id)
    return [
        PaymentHistorySchema(
            created_at=item.created_at,
            amount=Decimal(item.amount),
            status=item.status
        ) for item in payments
    ]


async def service_get_payment_history_admin(
    db: AsyncSession,
    user_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[PaymentResponseSchema]:
    logger.info(
        f"Fetching payment history for admin with filters - user_id: {user_id}, "
        f"status: {status}, start_date: {start_date}, end_date: {end_date}"
    )
    payment_history = await repo_get_payment_history_admin(
        db=db,
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

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


async def service_handle_stripe_webhook(
        event: Event,
        db: AsyncSession,
        email_service: EmailService,
        background_tasks: BackgroundTasks
) -> Dict[str, str]:
    logger.info(f"Handling Stripe webhook event: {event.type}")
    if event.type == "checkout.session.completed":
        session = event.data.object
        payment_data = CreatePaymentSchema(
            user_id=int(session["metadata"]["user_id"]),
            order_id=int(session["metadata"]["order_id"]),
            status=PaymentStatus.SUCCESSFUL,
            amount=Decimal(session["metadata"]["total_amount"]),
            external_payment_id=session["payment_intent"]
        )

        new_payment = await repo_create_payment_record(
            db, payment_data.model_dump()
        )
        logger.info(f"Payment created successfully for order_id: {session['metadata']['order_id']}")

        order = await repo_get_order_by_id(
            db, int(session["metadata"]["order_id"])
        )
        if order:
            await repo_update_order_status(db, order, StatusEnum.PAID)
            await repo_create_payment_items(db, order.items, new_payment.id)

        user_email = session["metadata"]["user_email"]
        background_tasks.add_task(
            email_service.send_payment_confirmation_email,
            recipient_email=user_email,
            order_id=session["metadata"]["order_id"]
        )

        return {"status": "success", "message": "Payment created"}

    elif event.type in ["checkout.session.async_payment_failed", "checkout.session.payment_failed"]:
        session = event.data.object
        payment_data = CreatePaymentSchema(
            user_id=int(session["metadata"]["user_id"]),
            order_id=int(session["metadata"]["order_id"]),
            status=PaymentStatus.CANCELED,
            amount=Decimal(session["metadata"]["total_amount"]),
            external_payment_id=session["payment_intent"]
        )

        new_payment = await repo_create_payment_record(
            db, payment_data.model_dump()
        )
        logger.info(f"Payment failed for order_id: {session['metadata']['order_id']}")

        user_email = session["metadata"]["user_email"]
        background_tasks.add_task(
            email_service.send_payment_cancellation_email,
            recipient_email=user_email,
            order_id=session["metadata"]["order_id"]
        )

        return {"status": "cancel", "message": "Payment cancelled"}


async def service_create_stripe_payment_session(
        order: OrderModel,
        user: UserModel,
        request: Request,
) -> str | None:
    logger.info(f"Creating Stripe payment session for order_id: {order.id} and user_id: {user.id}")
    unit_amount = order.total_amount
    if unit_amount <= 0:
        logger.warning(f"Invalid total sum for order_id: {order.id}")
        raise HTTPException(status_code=400, detail="Invalid total sum.")

    base_url = str(request.base_url).rstrip("/")
    success_url = f"{base_url}/api/v1/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/api/v1/payments/cancel"

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{item.movie.name} - Order #{order.id}"
                        },
                        "unit_amount": int(item.price_at_order * 100)
                    },
                    "quantity": 1,
                } for item in order.items
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": order.id,
                "user_id": user.id,
                "user_email": user.email,
                "total_amount": unit_amount
            },
        )
        logger.info(f"Stripe payment session created successfully for order_id: {order.id}")
        return session.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe payment session creation failed for order_id: {order.id}. Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
