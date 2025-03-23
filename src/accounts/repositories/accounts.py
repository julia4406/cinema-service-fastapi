from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import UserModel, ProfileModel, UserGroupModel
from src.database.models.accounts import UserGroupEnum
from src.accounts.schemas import UserCreateRequestSchema


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

    async def create_user(self, user: UserCreateRequestSchema) -> UserModel:
        group_result = await self.db.execute(
            select(UserGroupModel).filter_by(name=UserGroupEnum.USER)
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise ValueError("Default user group not found in database")

        db_user = UserModel(**user.model_dump(), group_id=group.id)
        self.db.add(db_user)
        await self.db.flush()

        db_profile = ProfileModel(user_id=db_user.id)
        self.db.add(db_profile)

        await self.db.commit()
        await self.db.refresh(db_user)
        await self.db.refresh(db_profile)
        return db_user


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
