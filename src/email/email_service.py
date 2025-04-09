from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.config.logging_settings import logger
from src.config.settings import Settings
from src.email.config import get_fastmail
from src.email.constants import (
    ACTIVATION_EMAIL_BODY,
    ACTIVATION_EMAIL_SUBJECT,
    PAYMENT_CANCELLATION_BODY,
    PAYMENT_CANCELLATION_SUBJECT,
    PAYMENT_CONFIRMATION_BODY,
    PAYMENT_CONFIRMATION_SUBJECT,
    RESET_PASSWORD_BODY,
    RESET_PASSWORD_SUBJECT,
)

settings = Settings()


class EmailService:
    def __init__(self, mail: FastMail = get_fastmail()) -> None:
        self.mail = mail

    async def send_email(self, recipient_email: EmailStr, subject: str, body: str) -> None:
        logger.info(f"Sending email to {recipient_email} with subject '{subject}'")
        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            subtype=MessageType.plain
        )
        await self.mail.send_message(message)
        logger.info(f"Email sent to {recipient_email} with subject '{subject}'")

    async def send_activation_email(self, recipient_email: EmailStr, token: str) -> None:
        activation_url = f"{settings.SERVICE_URL}auth/activate/{token}"
        body = ACTIVATION_EMAIL_BODY.format(activation_url=activation_url)
        logger.info(f"Sending activation email to {recipient_email}")
        await self.send_email(recipient_email, ACTIVATION_EMAIL_SUBJECT, body)

    async def send_reset_email(self, recipient_email: EmailStr, token: str) -> None:
        reset_url = f"{settings.SERVICE_URL}auth/reset-password/{token}"
        body = RESET_PASSWORD_BODY.format(reset_url=reset_url)
        logger.info(f"Sending reset password email to {recipient_email}")
        await self.send_email(recipient_email, RESET_PASSWORD_SUBJECT, body)

    async def send_payment_confirmation_email(self, recipient_email: EmailStr, order_id: int) -> None:
        body = PAYMENT_CONFIRMATION_BODY.format(order_id=order_id)
        logger.info(f"Sending payment confirmation email to {recipient_email}")
        await self.send_email(recipient_email, PAYMENT_CONFIRMATION_SUBJECT, body)

    async def send_payment_cancellation_email(self, recipient_email: EmailStr, order_id: int) -> None:
        body = PAYMENT_CANCELLATION_BODY.format(order_id=order_id)
        logger.info(f"Sending payment cancellation email to {recipient_email}")
        await self.send_email(recipient_email, PAYMENT_CANCELLATION_SUBJECT, body)


def get_email_service() -> EmailService:
    return EmailService()
