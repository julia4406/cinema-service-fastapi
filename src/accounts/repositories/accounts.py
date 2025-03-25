import boto3
from pydantic import EmailStr
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from accounts.schemas.accounts import UserAdminUpdateRequest, UserAdminCreateRequest
from src.database.models import UserModel, ProfileModel, UserGroupModel
from src.database.models.accounts import UserGroupEnum
from src.accounts.schemas import UserCreateRequest
from src.config.settings import Settings


settings = Settings()
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY
)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: EmailStr) -> UserModel | None:
        result = await self.db.execute(select(UserModel).filter_by(email=email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> UserModel | None:
        result = await self.db.execute(select(UserModel).filter_by(id=user_id))
        return result.scalar_one_or_none()

    async def is_email_exists(self, email: EmailStr) -> bool:
        result = await self.db.execute(select(UserModel).filter_by(email=email))
        return result.scalar_one_or_none() is not None

    async def is_user_active(self, user_id: int) -> bool:
        result = await self.db.execute(select(UserModel.is_active).filter_by(id=user_id))
        is_active_status = result.scalar_one_or_none()
        return is_active_status

    async def set_user_active(self, user_id: int) -> None:
        result = await self.db.execute(select(UserModel).filter_by(id=user_id))
        user = result.scalar_one_or_none()
        user.is_active = True

        await self.db.commit()
        await self.db.refresh(user)

    async def get_or_create_group(self, group_name: UserGroupEnum) -> UserGroupModel:
        group_result = await self.db.execute(
            select(UserGroupModel).filter_by(name=group_name.value)
        )
        group = group_result.scalar_one_or_none()
        if not group:
            group = UserGroupModel(name=group_name.value)
            self.db.add(group)
            await self.db.flush()
        return group

    async def create_user(self, user: UserCreateRequest) -> UserModel:
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

    async def create_user_by_admin(self, user: UserAdminCreateRequest) -> UserModel:
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

    async def update_user(self, user_id: int, user_data: UserAdminUpdateRequest):
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

    async def delete_user(self, user_id: int):
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        await self.db.delete(user)
        await self.db.commit()


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> ProfileModel | None:
        result = await self.db.execute(select(ProfileModel).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: int) -> ProfileModel:
        profile = ProfileModel(user_id=user_id)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update(self, profile: ProfileModel, data: dict) -> ProfileModel:
        for key, value in data.items():
            if value is not None:
                if key == "gender" and isinstance(value, str):
                    setattr(profile, key, value.upper())
                else:
                    setattr(profile, key, value)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete(self, profile: ProfileModel) -> None:
        await self.db.delete(profile)
        await self.db.commit()

    async def update_avatar(self, profile: ProfileModel, avatar_file: UploadFile, user_id: int) -> ProfileModel | None:
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

        try:
            s3_client.upload_fileobj(
                avatar_file.file,
                settings.S3_BUCKET,
                file_key
            )
        except Exception as e:
            raise ValueError(f"Failed to upload avatar to S3: {str(e)}")
        finally:
            await avatar_file.close()

        avatar_url = f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{file_key}"
        profile.avatar = avatar_url
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
