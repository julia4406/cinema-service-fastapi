from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from accounts.repositories.accounts import UserRepository
from accounts.repositories.tokens import ActivationTokensRepository
from accounts.services.email_service import EmailService
from src.database.models.accounts import UserModel
from src.accounts.schemas import UserCreateResponseSchema, UserCreateRequestSchema
from src.accounts.utils import hash_password


class AccountsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activation_token_repo = ActivationTokensRepository(db)
        self.email_service = EmailService()

    async def register_user(self, user: UserCreateRequestSchema) -> UserCreateResponseSchema:
        if await self.user_repo.is_email_exists(user.email):
            raise ValueError("This email is already registered")

        hashed_password = hash_password(user.password)

        user = UserCreateRequestSchema(email=user.email, password=hashed_password)

        new_user = await self.user_repo.create_user(user)
        activation_token = await self.activation_token_repo.create_activation_token(user_id=new_user.id)

        await self.email_service.send_activation_email(user.email, activation_token.token)

        return UserCreateResponseSchema(
            id=new_user.id,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            message="Activation link has been sent to your email",
        )

    async def activate_user(self, token: str) -> dict:
        activation_token = await self.activation_token_repo.get_activation_token(token)
        if not activation_token or activation_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            raise ValueError("Invalid activation token")

        user_id = activation_token.user_id

        if await self.user_repo.is_user_active(user_id=user_id):
            await self.activation_token_repo.delete_activation_token(token)
            raise ValueError("This user is already active")

        await self.user_repo.set_user_active(user_id=user_id)
        await self.activation_token_repo.delete_activation_token(token)

        return {"message": "Account has been activated"}

    async def resend_activation(self, email: EmailStr) -> dict:
        user_result = await self.db.execute(select(UserModel).filter_by(email=email))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        if await self.user_repo.is_user_active(user.id):
            raise ValueError("This user is already active")

        old_token = await self.activation_token_repo.get_activation_token_by_user_id(user.id)

        if old_token:
            await self.activation_token_repo.delete_activation_token(old_token.token)

        new_token = await self.activation_token_repo.create_activation_token(user.id)
        await self.email_service.send_activation_email(email, new_token.token)
        return {"message": "New activation token has been sent"}
