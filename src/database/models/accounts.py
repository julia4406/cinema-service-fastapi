import enum
from datetime import datetime

from sqlalchemy import Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class UserGroupEnum(str, enum.Enum):
   USER = "user"
   MODERATOR = "moderator"
   ADMIN = "admin"


class UserGroupModel(Base):
   __tablename__ = "user_groups"

   id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
   name: Mapped[UserGroupEnum] = mapped_column(
      Enum(UserGroupEnum), nullable=False, unique=True
   )

   users: Mapped[list["UserModel"]] = relationship(
      "UserModel", back_populates="group"
   )


class UserModel(Base):
   __tablename__ = "users"

   id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
   email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
   _hashed_password: Mapped[str] = mapped_column(nullable=False)
   is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
   created_at: Mapped[datetime] = mapped_column(
      server_default=func.now(), nullable=False
   )
   updated_at: Mapped[datetime] = mapped_column(
      server_default=func.now(), onupdate=func.now(), nullable=False
   )

   group_id: Mapped[int] = mapped_column(
      ForeignKey("user_groups.id", ondelete="CASCADE"),
      nullable=False
   )
   group: Mapped["UserGroupModel"] = relationship(
      "UserGroupModel", back_populates="users"
   )

   profile: Mapped["ProfileModel | None"] = relationship(
       "UserProfileModel",
       back_populates="user",
       cascade="all, delete-orphan"
   )
