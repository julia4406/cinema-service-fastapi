from datetime import datetime
from typing import List

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    DateTime,
    func, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.database.models import Base, UserModel, MovieModel

from database.validators.purchased import validate_movie_not_already_purchased
from database.validators.shopping_carts import (
    validate_movie_not_in_cart,
    validate_movie_not_in_purchases
)

UserCartsModel = Table(
    "user_carts",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ),
    Column(
        "cart_id",
        ForeignKey("carts.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    ),
)

UserPurchasesModel = Table(
    "user_purchases",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "purchased_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
)


class ShoppingCartModel(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="shopping_cart",
        uselist=False,
    )

    items: Mapped[List["CartItemModel"]] = relationship(
        "CartItemModel",
        back_populates="cart",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ShoppingCartModel(id={self.id}, user_id={self.user_id})>"


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    cart: Mapped["ShoppingCartModel"] = relationship(
        "ShoppingCartModel",
        back_populates="items"
    )
    movie: Mapped["MovieModel"] = relationship(
        "MovieModel",
        back_populates="cart_items"
    )

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "movie_id",
            name="unique_cart_movie_constraint"
        ),
    )

    def __repr__(self):
        return (f"<CartItemModel(id={self.id},"
                f" cart_id={self.cart_id},"
                f" movie_id={self.movie_id})>")

    @validates("movie_id")
    def validate_movie(self, key, movie_id):
        validate_movie_not_in_purchases(self, movie_id)
        validate_movie_not_in_cart(self, movie_id)
        return movie_id


class PurchasedModel(Base):
    __tablename__ = "purchased"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="purchases"
    )
    movie: Mapped["MovieModel"] = relationship(
        "MovieModel",
        back_populates="purchases"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "movie_id",
            name="unique_user_movie_purchase"
        ),
    )

    @validates("movie_id")
    def validate_movie_not_already_purchased(self, key, movie_id):
        return validate_movie_not_already_purchased(self, movie_id)

    def __repr__(self):
        return f"<PurchasedModel(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id})>"
