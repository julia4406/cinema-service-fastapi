from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from database.models.accounts import UserModel
from database.models.base import Base


class TokenBaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    expires_at: Mapped[datetime]

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


class ActivationTokenModel(TokenBaseModel):
    __tablename__ = "activation_tokens"

    user: Mapped[UserModel] = relationship("UserModel", back_populates="activation_token")

    __table_args__ = (UniqueConstraint("user_id"),)


class PasswordResetTokenModel(TokenBaseModel):
    __tablename__ = "password_reset_tokens"

    user: Mapped[UserModel] = relationship("UserModel", back_populates="password_reset_token")

    __table_args__ = (UniqueConstraint("user_id"),)


class RefreshTokenModel(TokenBaseModel):
    __tablename__ = "refresh_tokens"

    user: Mapped[UserModel] = relationship("UserModel", back_populates="refresh_tokens")
