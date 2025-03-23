from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.repositories.accounts import UserRepository, ProfileRepository
from accounts.repositories.tokens import (
    ActivationTokensRepository,
    RefreshTokensRepository,
    PasswordResetTokenRepository
)
from accounts.services.email_service import EmailService
from accounts.security.jwt import JWTAuthManager
from src.database.models import UserModel, ProfileModel
from accounts.validators.accounts import validate_password_strength
from accounts.schemas import (
    UserCreateResponseSchema,
    UserCreateRequestSchema,
    JWTTokenResponse,
    UserLoginRequestSchema,
    RefreshTokenRequest
)


class AccountsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.activation_token_repo = ActivationTokensRepository(db)
        self.email_service = EmailService()
        self.jwt_service = JWTAuthManager()
        self.reset_token_repo = PasswordResetTokenRepository(db)

    async def register_user(self, user: UserCreateRequestSchema) -> UserCreateResponseSchema:
        if await self.user_repo.is_email_exists(user.email):
            raise ValueError("This email is already registered")

        user = UserCreateRequestSchema(email=user.email, password=user.password)

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
        user = await self.user_repo.get_by_email(email)
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

    async def login_user(self, user: UserLoginRequestSchema) -> JWTTokenResponse:
        db_user = await self.user_repo.get_by_email(user.email)
        if not db_user or not db_user.verify_password(user.password):
            raise ValueError("Invalid credentials")

        await RefreshTokensRepository(self.db).delete_all_by_user_id(db_user.id)

        access_token = self.jwt_service.create_access_token(db_user)
        refresh_token = await self.jwt_service.create_refresh_token(db_user, self.db)

        return JWTTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_access_token(self, refresh_token: RefreshTokenRequest) -> JWTTokenResponse:
        refresh_token = refresh_token.refresh_token
        user = await self.jwt_service.verify_refresh_token(refresh_token, db=self.db)
        await RefreshTokensRepository(self.db).delete_all_by_user_id(user.id)

        new_access_token = self.jwt_service.create_access_token(user)
        new_refresh_token = await self.jwt_service.create_refresh_token(user, self.db)

        return JWTTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def change_password(self, current_user: UserModel, old_password: str, new_password: str) -> dict:
        if not current_user.verify_password(old_password):
            raise ValueError("The old password is incorrect")
        validate_password_strength(new_password)
        current_user.password = new_password
        await self.db.commit()
        await self.db.refresh(current_user)
        return {"message": "Password has been changed successfully"}

    async def forgot_password(self, email: EmailStr) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("The user does not exist")

        existing_token = await self.reset_token_repo.get_reset_token_by_user_id(user.id)
        if existing_token:
            await self.reset_token_repo.delete_reset_token(existing_token.token)

        reset_token = await self.reset_token_repo.create_reset_token(user.id)
        await self.email_service.send_reset_email(email, reset_token.token)
        return {"message": "The letter for resetting password has been sent to your email"}

    async def reset_password(self, token: str, new_password: str) -> dict:
        reset_token = await self.reset_token_repo.verify_reset_token(token)

        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            raise ValueError("The user does not exist")

        validate_password_strength(new_password)
        user.password = new_password

        await self.db.commit()
        await self.reset_token_repo.delete_reset_token(token)
        return {"message": "Password has been changed successfully"}


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = ProfileRepository(db)

    async def get_profile(self, current_user: UserModel) -> ProfileModel:
        profile = await self.profile_repo.get_by_user_id(current_user.id)
        if not profile:
            raise ValueError("Profile is not found")
        return profile

    async def update_profile(self, current_user: UserModel, profile_data) -> ProfileModel:
        profile = await self.get_profile(current_user)
        updated_profile = await self.profile_repo.update(profile, profile_data.model_dump(exclude_unset=True))
        return updated_profile
