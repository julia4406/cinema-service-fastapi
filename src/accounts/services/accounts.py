from datetime import datetime, timezone

from fastapi import UploadFile
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.accounts.repositories.accounts import ProfileRepository, UserRepository
from src.accounts.repositories.tokens import (
    ActivationTokensRepository,
    PasswordResetTokenRepository,
    RefreshTokensRepository,
)
from src.accounts.schemas import (
    JWTTokenResponse,
    RefreshTokenRequest,
    UserCreateRequest,
    UserCreateResponse,
    UserLoginRequest,
)
from src.accounts.schemas.accounts import (
    ProfileUpdateRequest,
    UserAdminCreateRequest,
    UserAdminResponse,
    UserAdminUpdateRequest,
)
from src.accounts.security.jwt import JWTAuthManager
from src.accounts.validators.accounts import validate_password_strength
from src.config.logging_settings import logger
from src.database.models import ProfileModel, UserModel
from src.email.email_service import EmailService


class AccountsService:
    def __init__(
            self,
            user_repo: UserRepository,
            activation_token_repo: ActivationTokensRepository,
            email_service: EmailService,
            jwt_service: JWTAuthManager,
            reset_token_repo: PasswordResetTokenRepository,
    ) -> None:
        self.db = user_repo.db
        self.user_repo = user_repo
        self.activation_token_repo = activation_token_repo
        self.email_service = email_service
        self.jwt_service = jwt_service
        self.reset_token_repo = reset_token_repo

    async def get_by_email(self, email: EmailStr) -> UserModel:
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found.")
            raise ValueError("User not found")
        return user

    async def register_user(self, user: UserCreateRequest) -> UserCreateResponse:
        if await self.user_repo.is_email_exists(user.email):
            logger.warning(f"Email {user.email} is already registered.")
            raise ValueError("This email is already registered")

        new_user = await self.user_repo.create_user(user)
        activation_token = await self.activation_token_repo.create_activation_token(user_id=new_user.id)

        await self.email_service.send_activation_email(user.email, activation_token.token)

        logger.info(f"User with email {user.email} registered successfully.")
        return UserCreateResponse(
            id=new_user.id,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            message="Activation link has been sent to your email",
        )

    async def register_user_by_admin(self, user: UserAdminCreateRequest) -> UserAdminResponse:
        if await self.user_repo.is_email_exists(user.email):
            logger.warning(f"Email {user.email} is already registered.")
            raise ValueError("This email is already registered")

        new_user = await self.user_repo.create_user_by_admin(user)
        if not new_user.is_active:
            activation_token = await self.activation_token_repo.create_activation_token(user_id=new_user.id)
            await self.email_service.send_activation_email(user.email, activation_token.token)

        result = await self.db.execute(
            select(UserModel)
            .filter_by(id=new_user.id)
            .options(joinedload(UserModel.group))
        )
        user_with_group = result.scalar_one_or_none()

        if not user_with_group:
            logger.warning(f"User with ID {new_user.id} not found after registration.")
            raise ValueError("User not found")

        logger.info(f"Admin registered user {user_with_group.email} with group {user_with_group.group.name}.")
        return UserAdminResponse(
            id=user_with_group.id,
            email=user_with_group.email,
            is_active=user_with_group.is_active,
            group=user_with_group.group.name,
        )

    async def update_user(self, user_id: int, user_data: UserAdminUpdateRequest) -> UserAdminResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise ValueError("User not found")

        if user_data.email and user_data.email != user.email:
            if await self.user_repo.is_email_exists(user_data.email):
                logger.warning(f"Email {user_data.email} is already registered.")
                raise ValueError("This email is already registered")

        updated_user = await self.user_repo.update_user(user_id, user_data)

        result = await self.db.execute(
            select(UserModel)
            .filter_by(id=updated_user.id)
            .options(joinedload(UserModel.group))
        )
        user_with_group = result.scalar_one_or_none()
        if not user_with_group:
            logger.warning(f"User with ID {updated_user.id} not found after update.")
            raise ValueError("User not found after update")

        logger.info(f"User {updated_user.email} updated successfully.")
        return UserAdminResponse(
            id=updated_user.id,
            email=updated_user.email,
            is_active=updated_user.is_active,
            group=updated_user.group.name,
        )

    async def delete_user(self, user_id: int, current_user: UserModel) -> None:
        if user_id == current_user.id:
            logger.warning("Attempted to delete the current user.")
            raise ValueError("Cannot delete yourself")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            raise ValueError("User not found")

        await self.user_repo.delete_user(user_id)
        logger.info(f"User with ID {user_id} deleted successfully.")

    async def activate_user(self, token: str) -> dict:
        activation_token = await self.activation_token_repo.get_activation_token(token)
        if not activation_token or activation_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            logger.warning(f"Invalid or expired activation token {token}.")
            raise ValueError("Invalid activation token")

        user_id = activation_token.user_id

        if await self.user_repo.is_user_active(user_id=user_id):
            await self.activation_token_repo.delete_activation_token(token)
            logger.warning(f"User with ID {user_id} is already active.")
            raise ValueError("This user is already active")

        await self.user_repo.set_user_active(user_id=user_id)
        await self.activation_token_repo.delete_activation_token(token)

        logger.info(f"User with ID {user_id} activated successfully.")
        return {"message": "Account has been activated"}

    async def resend_activation(self, email: EmailStr) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found.")
            raise ValueError("User not found")

        if await self.user_repo.is_user_active(user.id):
            logger.warning(f"User with email {email} is already active.")
            raise ValueError("This user is already active")

        old_token = await self.activation_token_repo.get_activation_token_by_user_id(user.id)

        if old_token:
            await self.activation_token_repo.delete_activation_token(old_token.token)

        new_token = await self.activation_token_repo.create_activation_token(user.id)
        await self.email_service.send_activation_email(email, new_token.token)
        logger.info(f"New activation token sent to user {email}.")
        return {"message": "New activation token has been sent"}

    async def login_user(self, user: UserLoginRequest) -> JWTTokenResponse:
        db_user = await self.user_repo.get_by_email(user.email)
        if not db_user or not db_user.verify_password(user.password):
            logger.warning(f"Invalid credentials for user {user.email}.")
            raise ValueError("Invalid credentials")

        await RefreshTokensRepository(self.db).delete_all_by_user_id(db_user.id)

        access_token = self.jwt_service.create_access_token(db_user)
        refresh_token = await self.jwt_service.create_refresh_token(db_user, self.db)

        logger.info(f"User {user.email} logged in successfully.")
        return JWTTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def logout_user(self, user: UserModel) -> None:
        await RefreshTokensRepository(self.db).delete_all_by_user_id(user.id)
        logger.info(f"User {user.email} logged out successfully.")

    async def refresh_access_token(self, refresh_token: RefreshTokenRequest) -> JWTTokenResponse:
        refresh_token = refresh_token.refresh_token
        user = await self.jwt_service.verify_refresh_token(refresh_token, db=self.db)
        await RefreshTokensRepository(self.db).delete_all_by_user_id(user.id)

        new_access_token = self.jwt_service.create_access_token(user)
        new_refresh_token = await self.jwt_service.create_refresh_token(user, self.db)

        logger.info(f"Access token refreshed for user {user.email}.")
        return JWTTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def change_password(self, current_user: UserModel, old_password: str, new_password: str) -> dict:
        if not current_user.verify_password(old_password):
            logger.warning(f"Incorrect old password for user {current_user.email}.")
            raise ValueError("The old password is incorrect")
        validate_password_strength(new_password)
        current_user.password = new_password
        await self.db.commit()
        await self.db.refresh(current_user)
        logger.info(f"Password changed successfully for user {current_user.email}.")
        return {"message": "Password has been changed successfully"}

    async def forgot_password(self, email: EmailStr) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found.")
            raise ValueError("The user does not exist")

        existing_token = await self.reset_token_repo.get_reset_token_by_user_id(user.id)
        if existing_token:
            await self.reset_token_repo.delete_reset_token(existing_token.token)

        reset_token = await self.reset_token_repo.create_reset_token(user.id)
        await self.email_service.send_reset_email(email, reset_token.token)
        logger.info(f"Password reset email sent to user {email}.")
        return {"message": "The letter for resetting password has been sent to your email"}

    async def reset_password(self, token: str, new_password: str) -> dict:
        reset_token = await self.reset_token_repo.verify_reset_token(token)

        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            logger.warning(f"User not found for reset token {token}.")
            raise ValueError("The user does not exist")

        validate_password_strength(new_password)
        user.password = new_password

        await self.db.commit()
        await self.reset_token_repo.delete_reset_token(token)
        logger.info(f"Password reset successfully for user {user.email}.")
        return {"message": "Password has been changed successfully"}


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository) -> None:
        self.db = profile_repo.db
        self.profile_repo = profile_repo

    async def get_profile(self, current_user: UserModel) -> ProfileModel:
        logger.info(f"Fetching profile for user: {current_user.email}")
        profile = await self.profile_repo.get_by_user_id(current_user.id)
        if not profile:
            logger.warning(f"Profile for user {current_user.email} not found.")
            raise ValueError("Profile is not found")
        return profile

    async def update_profile(
            self, current_user: UserModel, profile_data: ProfileUpdateRequest
    ) -> ProfileModel:
        logger.info(f"Updating profile for user: {current_user.email}")
        profile = await self.get_profile(current_user)
        updated_profile = await self.profile_repo.update(profile, profile_data.model_dump(exclude_unset=True))
        logger.info(f"Profile updated for user {current_user.email}.")
        return updated_profile

    async def upload_avatar(self, current_user: UserModel, avatar_file: UploadFile) -> ProfileModel:
        logger.info(f"Uploading avatar for user: {current_user.email}")
        profile = await self.get_profile(current_user)
        updated_profile = await self.profile_repo.update_avatar(profile, avatar_file, current_user.id)
        logger.info(f"Avatar uploaded for user {current_user.email}.")
        return updated_profile
