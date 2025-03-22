import datetime

from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database.models.base import Base


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
        if self.user:
            for purchase in self.user.purchases:
                if purchase.movie_id == movie_id and purchase is not self:
                    raise ValueError(
                        f"Movie with id {movie_id} is already purchased by user {self.user_id}"
                    )
        return movie_id

    def __repr__(self):
        return f"<PurchasedModel(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id})>"
