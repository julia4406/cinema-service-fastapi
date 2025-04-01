from pydantic import EmailStr
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.accounts.schemas.accounts import (
    UserAdminUpdateRequest, UserAdminCreateRequest
)
from src.database.models import UserModel, ProfileModel, UserGroupModel
from src.database.models.accounts import UserGroupEnum
from src.accounts.s3_service import S3Service
from src.accounts.schemas import UserCreateRequest
from src.config.settings import Settings
from src.config.logging_settings import logger


settings = Settings()


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: EmailStr) -> UserModel | None:
        try:
            result = await self.db.execute(select(UserModel).filter_by(email=email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise

    async def get_by_id(self, user_id: int) -> UserModel | None:
        try:
            result = await self.db.execute(select(UserModel).filter_by(id=user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by id {user_id}: {e}")
            raise

    async def is_email_exists(self, email: EmailStr) -> bool:
        try:
            result = await self.db.execute(select(UserModel).filter_by(email=email))
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking if email {email} exists: {e}")
            raise

    async def is_user_active(self, user_id: int) -> bool:
        try:
            result = await self.db.execute(select(UserModel.is_active).filter_by(id=user_id))
            is_active_status = result.scalar_one_or_none()
            return is_active_status
        except Exception as e:
            logger.error(f"Error checking if user {user_id} is active: {e}")
            raise

    async def set_user_active(self, user_id: int) -> None:
        try:
            result = await self.db.execute(select(UserModel).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            if user:
                user.is_active = True
                await self.db.commit()
                await self.db.refresh(user)
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            raise

    async def get_or_create_group(self, group_name: UserGroupEnum) -> UserGroupModel:
        try:
            group_result = await self.db.execute(
                select(UserGroupModel).filter_by(name=group_name.value)
            )
            group = group_result.scalar_one_or_none()
            if not group:
                group = UserGroupModel(name=group_name.value)
                self.db.add(group)
                await self.db.flush()
            return group
        except Exception as e:
            logger.error(f"Error fetching or creating group {group_name}: {e}")
            raise

    async def create_user(self, user: UserCreateRequest) -> UserModel:
        try:
            group = await self.get_or_create_group(UserGroupEnum.USER)
            db_user = UserModel(**user.model_dump(), group_id=group.id)
            self.db.add(db_user)
            await self.db.flush()

            db_profile = ProfileModel(user_id=db_user.id)
            self.db.add(db_profile)

            await self.db.commit()
            await self.db.refresh(db_user)
            await self.db.refresh(db_profile)
            return db_user
        except Exception as e:
            logger.error(f"Error creating user {user.email}: {e}")
            raise

    async def create_user_by_admin(self, user: UserAdminCreateRequest) -> UserModel:
        try:
            group = await self.get_or_create_group(user.group)

            db_user = UserModel(
                email=user.email,
                is_active=user.is_active,
                group_id=group.id,
            )
            db_user.password = user.password
            self.db.add(db_user)
            await self.db.flush()

            db_profile = ProfileModel(user_id=db_user.id)
            self.db.add(db_profile)

            await self.db.commit()
            await self.db.refresh(db_user)
            await self.db.refresh(db_profile)
            return db_user
        except Exception as e:
            logger.error(f"Error creating user by admin {user.email}: {e}")
            raise

    async def update_user(self, user_id: int, user_data: UserAdminUpdateRequest):
        try:
            user = await self.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            update_data = user_data.model_dump(exclude_unset=True)
            if "group" in update_data:
                group = await self.get_or_create_group(update_data.pop("group"))
                user.group_id = group.id

            for key, value in update_data.items():
                setattr(user, key, value)

            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, user_id: int):
        try:
            user = await self.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            await self.db.delete(user)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise


class ProfileRepository:
    def __init__(self, db: AsyncSession, s3_service: S3Service):
        self.db = db
        self.s3_service = s3_service

    async def get_by_user_id(self, user_id: int) -> ProfileModel | None:
        try:
            result = await self.db.execute(select(ProfileModel).filter_by(user_id=user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            raise

    async def create(self, user_id: int) -> ProfileModel:
        try:
            profile = ProfileModel(user_id=user_id)
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except Exception as e:
            logger.error(f"Error creating profile for user {user_id}: {e}")
            raise

    async def update(self, profile: ProfileModel, data: dict) -> ProfileModel:
        try:
            for key, value in data.items():
                if value is not None:
                    if key == "gender" and isinstance(value, str):
                        setattr(profile, key, value.upper())
                    else:
                        setattr(profile, key, value)
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except Exception as e:
            logger.error(f"Error updating profile {profile.user_id}: {e}")
            raise

    async def delete(self, profile: ProfileModel) -> None:
        try:
            await self.db.delete(profile)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting profile for user {profile.user_id}: {e}")
            raise

    async def update_avatar(self, profile: ProfileModel, avatar_file: UploadFile, user_id: int) -> ProfileModel | None:
        try:
            allowed_types = {"image/jpeg", "image/png"}
            max_size_mb = 8
            max_size_bytes = max_size_mb * 1024 * 1024

            if avatar_file.content_type not in allowed_types:
                raise ValueError("Avatar must be a JPEG or PNG image")

            file_size = avatar_file.size
            if file_size > max_size_bytes:
                raise ValueError(f"Avatar size must not exceed {max_size_mb} MB")

            file_extension = avatar_file.filename.split(".")[-1]
            file_key = f"avatars/{user_id}/{user_id}_avatar.{file_extension}"

            avatar_url = await self.s3_service.upload_file(avatar_file, file_key)

            profile.avatar = avatar_url
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except Exception as e:
            logger.error(f"Error updating avatar for user {user_id}: {e}")
            raise
