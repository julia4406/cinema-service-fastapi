from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from src.config.settings import Settings
from pydantic import EmailStr

settings = Settings()

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False
        )
        self.fm = FastMail(self.conf)

    async def send_activation_email(self, recipient_email: EmailStr, token: str) -> None:
        activation_url = f"{settings.SERVICE_URL}auth/activate/{token}"
        subject = "Activation email"

        body = (
            f"Hello!\n\n"
            f"Thank you for registering. To activate your account, "
            f"please follow this link: {activation_url}\n\n"
            f"The link is valid for 24 hours. If you did not register, please ignore this email."
        )

        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            subtype=MessageType.plain
        )

        await self.fm.send_message(message)

    async def send_reset_email(self, recipient_email: EmailStr, token: str) -> None:
        reset_url = f"{settings.SERVICE_URL}auth/reset-password/{token}"
        subject = "Password Reset Request"

        body = (
            f"Hello!\n\n"
            f"We received a request to reset your password. To proceed, "
            f"please follow this link: {reset_url}\n\n"
            f"The link is valid for 1 hour. If you did not request a password reset, please ignore this email."
        )

        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            subtype=MessageType.plain
        )

        await self.fm.send_message(message)
