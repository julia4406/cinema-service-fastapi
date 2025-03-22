import enum
from typing import TYPE_CHECKING, List
from datetime import datetime, date

from sqlalchemy import Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from typing import Optional

if TYPE_CHECKING:
    from database.models.tokens import (
        ActivationTokenModel,
        PasswordResetTokenModel,
        RefreshTokenModel,
    )


class GenderEnum(enum.Enum):
    MAN = "man"
    WOMAN = "woman"


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
        "UserModel",
        back_populates="group",
    )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    _hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("user_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    group: Mapped["UserGroupModel"] = relationship(
        "UserGroupModel",
        back_populates="users",
    )
    profile: Mapped["ProfileModel | None"] = relationship(
        "ProfileModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    activation_token: Mapped[Optional["ActivationTokenModel"]] = relationship(
        "ActivationTokenModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    password_reset_token: Mapped[
        Optional["PasswordResetTokenModel"]] = relationship(
        "PasswordResetTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    shopping_cart: Mapped[Optional["ShoppingCartModel"]] = relationship(
        "ShoppingCartModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    purchases: Mapped[List["PurchasedModel"]] = relationship(
        "PurchasedModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum))
    avatar: Mapped[str | None] = mapped_column()
    date_of_birth: Mapped[date | None] = mapped_column()
    info: Mapped[str | None] = mapped_column()

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="profile",
    )
