from datetime import datetime
from typing import List

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
# from database.validators import (
#     validate_movie_not_in_orders,
#     validate_movie_not_in_cart
# )


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
        back_populates="carts",
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
    # movie_id: Mapped[int] = mapped_column(
    #     ForeignKey("movies.id", ondelete="CASCADE"),
    #     nullable=False
    # )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    cart: Mapped["ShoppingCartModel"] = relationship("ShoppingCartModel")
    # movie = relationship("MovieModel")

    # __table_args__ = (
    #     UniqueConstraint(
    #         "cart_id",
    #         "movie_id",
    #         name="unique_cart_movie_constraint"
    #     ),
    # )

    # def __repr__(self):
    #     return (f"<CartItemModel(id={self.id},"
    #             f" cart_id={self.cart_id},"
    #             f" movie_id={self.movie_id})>")

    # @validates("movie_id")
    # def validate_movie(self, key, movie_id):
    #     validate_movie_not_in_orders(self, movie_id)
    #     validate_movie_not_in_cart(self, movie_id)
    #     return movie_id
