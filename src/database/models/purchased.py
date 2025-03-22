import datetime

from sqlalchemy import (
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint,
    Table,
    Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database.models.base import Base

# from database.validators.purchased import validate_movie_not_already_purchased

UserPurchasesModel = Table(
    "user_purchases",
    Base.metadata,
    Column("id", primary_key=True, autoincrement=True),
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
    ),
    UniqueConstraint("user_id", "movie_id", name="unique_user_movie_purchase")
)


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

    # @validates("movie_id")
    # def validate_movie_not_already_purchased(self, key, movie_id):
    #     return validate_movie_not_already_purchased(self, movie_id)

    def __repr__(self):
        return f"<PurchasedModel(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id})>"
