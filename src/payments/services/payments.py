from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import stripe
from fastapi import BackgroundTasks, HTTPException, Request
from stripe import Event

from config.settings import StripeSettings as stp
from src.config.logging_settings import logger
from src.database.models.accounts import UserModel
from src.database.models.orders import OrderModel, StatusEnum
from src.database.models.payments import PaymentStatus
from src.email.email_service import EmailService
from src.payments.repositories.payments import PaymentRepository
from src.payments.schemas.payments import CreatePaymentSchema, PaymentHistorySchema, PaymentResponseSchema


class PaymentService:
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo
        self.db = payment_repo.db

    async def get_user_payment_history(
            self, user_id: int
    ) -> List[PaymentHistorySchema]:
        logger.info(f"Fetching payment history for user_id: {user_id}")
        payments = await self.payment_repo.get_payment_history_by_user_id(user_id)
        return [
            PaymentHistorySchema(
                created_at=item.created_at,
                amount=Decimal(item.amount),
                status=item.status
            ) for item in payments
        ]


    async def get_admin_payment_history(
        self,
        user_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PaymentResponseSchema]:
        logger.info(
            f"Fetching payment history for admin with filters - user_id: {user_id}, "
            f"status: {status}, start_date: {start_date}, end_date: {end_date}"
        )
        payment_history = await self.payment_repo.get_payment_history_as_admin(
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


    async def handle_stripe_webhook(
            self,
            event: Event,
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

            new_payment = await self.payment_repo.create_payment_record(payment_data.model_dump())
            logger.info(f"Payment created for order_id: {session['metadata']['order_id']}")

            order = await self.payment_repo.get_order_by_id(int(session["metadata"]["order_id"]))
            if order:
                await self.payment_repo.update_order_status(order, StatusEnum.PAID)
                await self.payment_repo.create_payment_items(order.items, new_payment.id)

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

            await self.payment_repo.create_payment_record(payment_data.model_dump())
            logger.info(f"Payment failed for order_id: {session['metadata']['order_id']}")

            user_email = session["metadata"]["user_email"]
            background_tasks.add_task(
                email_service.send_payment_cancellation_email,
                recipient_email=user_email,
                order_id=session["metadata"]["order_id"]
            )

            return {"status": "cancel", "message": "Payment cancelled"}


    async def service_create_stripe_payment_session(
            self,
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
            stripe.api_key = stp.STRIPE_SECRET_KEY
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
