from datetime import datetime
from typing import Optional, List

import stripe
from fastapi import (
    APIRouter, HTTPException, Depends, Request, BackgroundTasks, Query
)
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_settings import logger
from src.config.settings import Settings
from src.payments.services.payments import (
    service_get_payment_history,
    service_get_payment_history_admin,
    service_create_stripe_payment_session,
    service_handle_stripe_webhook
)
from src.payments.schemas.payments import (
    PaymentHistorySchema,
    PaymentResponseSchema,
)
from src.database.models.accounts import UserModel, UserGroupEnum
from src.database.models.payments import PaymentStatus
from src.database.models.orders import OrderModel
from src.database.session_postgresql import get_postgresql_db
from src.email.email_service import EmailService, get_email_service
from src.accounts.dependencies import role_required


router = APIRouter()
settings = Settings()

@router.post("/webhook")
async def stripe_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        email_service: EmailService = Depends(get_email_service),
        db: AsyncSession = Depends(get_postgresql_db)
):
    logger.info("Received Stripe webhook request.")
    stripe_signature = request.headers.get("stripe-signature")
    if not stripe_signature:
        logger.warning("Missing Stripe signature in webhook request.")
        raise HTTPException(status_code=400, detail="No stripe signature")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
        logger.info(f"Successfully parsed Stripe event: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid Stripe payload: {str(e)}")
        return {"status": "error", "message": f"Invalid payload: {str(e)}"}, 400
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe signature.")
        return {"status": "error", "message": "Invalid signature"}, 400

    return await service_handle_stripe_webhook(
        event, db, email_service, background_tasks
    )


@router.post("/{order_id}")
async def create_payment(
        order_id: int,
        request: Request,
        current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
        db: AsyncSession = Depends(get_postgresql_db),
):
    logger.info(f"User {current_user.id} is creating a payment for order {order_id}.")
    order = await db.execute(select(OrderModel).filter_by(id=order_id))
    current_order = order.scalars().first()

    if not current_order:
        logger.warning(f"Order {order_id} not found.")
        raise HTTPException(status_code=400, detail="Order not found")

    user = await db.execute(select(UserModel).filter_by(id=current_order.user_id))
    user = user.scalars().first()

    payment_url = await service_create_stripe_payment_session(
        current_order, user, request
    )
    logger.info(f"Payment session created for order {order_id}.")
    return {"payment_url": payment_url}


@router.get("/success")
async def success_payment() -> JSONResponse:
    logger.info("Payment successfully completed.")
    return JSONResponse(
        content={"message": "The payment has been successfully completed."}
    )


@router.get("/cancel")
async def cancel_payment() -> JSONResponse:
    logger.info("Payment was canceled.")
    return JSONResponse(
        content={"message": "The payment has been canceled."}
    )


@router.get("/history", response_model=PaymentHistorySchema)
async def get_payments_history(
        current_user: UserModel = Depends(role_required(UserGroupEnum.USER)),
        db: AsyncSession = Depends(get_postgresql_db),
) -> List[PaymentHistorySchema]:
    logger.info(f"Fetching payment history for user {current_user.id}.")
    return await service_get_payment_history(db, current_user.id)


@router.get("/history/staff", response_model=PaymentResponseSchema)
async def get_payments_history(
        current_user: UserModel = Depends(role_required(UserGroupEnum.MODERATOR)),
        db: AsyncSession = Depends(get_postgresql_db),
        user_id: Optional[int] = Query(
            None, description="user ID for filtering."
        ),
        status: Optional[PaymentStatus] = Query(
            None, description="Filter by status successful, refunded, canceled."
        ),
        start_date: Optional[datetime] = Query(
            None, description="Start date (YYYY-MM-DD)."
        ),
        end_date: Optional[datetime] = Query(
            None, description="End date (YYYY-MM-DD)."
        )
) -> List[PaymentResponseSchema]:
    logger.info("Fetching payment history for staff.")
    return await service_get_payment_history_admin(
        db=db,
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
