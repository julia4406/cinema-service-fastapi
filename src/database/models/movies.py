import datetime
import enum
from typing import List
from uuid import UUID as UUIDType

from sqlalchemy import String, Float, Text, DECIMAL, UniqueConstraint, ForeignKey, Integer, DateTime, func, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database.models import Base


class ReactionType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class StarModel(Base):
    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    movies: Mapped[List["MovieModel"]] = relationship(
        "MovieModel",
        secondary="movies_stars_association",
        back_populates="stars",
        uselist=True,
    )


class GenreModel(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    movies: Mapped[List["MovieModel"]] = relationship(
        "MovieModel",
        secondary="movies_genres_association",
        back_populates="genres",
    )


class DirectorModel(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    movies: Mapped[List["MovieModel"]] = relationship(
        "MovieModel",
        secondary="movies_directors_association",
        back_populates="directors",
    )


class CertificationModel(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    movies: Mapped[List["MovieModel"]] = relationship("MovieModel", back_populates="certifications")


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="comments")


class UserFavoriteModel(Base):
    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="favorites")
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "movie_id"),)


class UserReactionModel(Base):
    __tablename__ = "reactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    reaction_type: Mapped[ReactionType] = mapped_column(Enum(ReactionType), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reactions")
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="reactions")

    __table_args__ = (UniqueConstraint("user_id", "movie_id"),)


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUIDType] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    time: Mapped[int] = mapped_column(nullable=False)
    imdb: Mapped[float] = mapped_column(nullable=False)
    votes: Mapped[int] = mapped_column(nullable=False)
    meta_score: Mapped[float] = mapped_column()
    gross: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))

    certification_id: Mapped[int] = mapped_column(ForeignKey("certifications.id"))
    certifications: Mapped[CertificationModel] = relationship("CertificationModel", back_populates="movies")

    comments: Mapped[List["CommentModel"]] = relationship("CommentModel", back_populates="movie")

    genres: Mapped[List["GenreModel"]] = relationship(
        "GenreModel", secondary="movies_genres_association", back_populates="movies"
    )

    directors: Mapped[List["DirectorModel"]] = relationship(
        "DirectorModel", secondary="movies_directors_association", back_populates="movies"
    )

    stars: Mapped[List["StarModel"]] = relationship(
        "StarModel", secondary="movies_stars_association", back_populates="movies"
    )

    favorites: Mapped[List["UserFavoriteModel"]] = relationship(
        "UserFavoriteModel", back_populates="movie"
    )

    reactions: Mapped[List["UserReactionModel"]] = relationship(
        "UserReactionModel", back_populates="movie"
    )

    cart_items: Mapped[List["CartItemModel"]] = relationship(
        "CartItemModel", back_populates="movie"
    )

    purchases: Mapped[List["PurchasedModel"]] = relationship(
        "PurchasedModel", back_populates="movie"
    )

    __table_args__ = (UniqueConstraint("name", "year", "time"),)


class MoviesGenresModel(Base):
    __tablename__ = "movies_genres_association"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)


class MoviesDirectorsModel(Base):
    __tablename__ = "movies_directors_association"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    director_id: Mapped[int] = mapped_column(ForeignKey("directors.id", ondelete="CASCADE"), primary_key=True)

class MoviesStarsModel(Base):
    __tablename__ = "movies_stars_association"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    star_id: Mapped[int] = mapped_column(ForeignKey("stars.id", ondelete="CASCADE"), primary_key=True)
