from typing import Optional, Any
from uuid import uuid4

from sqlalchemy import Result, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import now

from src.config.logging_settings import logger
from src.database.models import UserModel
from src.database.models.movies import (
    CertificationModel,
    DirectorModel,
    GenreModel,
    MovieModel,
    StarModel,
    UserReactionModel,
    UserFavoriteModel,
    MoviesStarsModel,
    MoviesDirectorsModel,
)
from src.database.models.shopping_carts import PurchasedModel
from src.movies.schemas.movies import MovieCreateSchema, MovieSortEnum


class MoviesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("MoviesRepository initialized")

    async def get_movies_paginated(
        self, page: int, per_page: int
    ) -> tuple[int, list[MovieModel]]:
        logger.info(f"Fetching paginated movies: page={page}, per_page={per_page}")
        offset = (page - 1) * per_page

        total_items = await self.db.scalar(select(func.count()).select_from(MovieModel))

        query = (
            select(MovieModel)
            .order_by(MovieModel.id)
            .offset(offset)
            .limit(per_page)
            .options(
                joinedload(MovieModel.genres),
                joinedload(MovieModel.stars),
                joinedload(MovieModel.directors),
            )
        )
        result = await self.db.execute(query)
        movies = result.unique().scalars().all()
        logger.info(f"Total movies found: {total_items}, Movies returned: {len(movies)}")
        return total_items, movies

    async def get_movie_by_id(self, movie_id: int) -> Optional[MovieModel]:
        logger.info(f"Fetching movie by ID: {movie_id}")
        result = await self.db.execute(
            select(MovieModel)
            .options(
                joinedload(MovieModel.certifications),
                joinedload(MovieModel.genres),
                joinedload(MovieModel.stars),
                joinedload(MovieModel.directors),
            )
            .filter(MovieModel.id == movie_id)
        )
        movie = result.scalars().first()
        if movie:
            logger.info(f"Movie found: {movie.name}")
        else:
            logger.warning(f"Movie with ID {movie_id} not found")
        return movie

    async def get_detail_movies_by_id(self, movie_id: int) -> Optional[MovieModel]:
        result = await self.db.execute(
            select(MovieModel)
            .options(
                joinedload(MovieModel.certifications),
                joinedload(MovieModel.genres),
                joinedload(MovieModel.stars),
                joinedload(MovieModel.directors),
            )
            .filter(MovieModel.id == movie_id)
        )
        return result.scalars().first()

    async def get_movie_by_name(
        self, movie_data: MovieCreateSchema
    ) -> Optional[MovieModel]:
        logger.info(f"Retrieving movie by name: {movie_data}")
        result = await self.db.execute(
            select(MovieModel).filter(MovieModel.name == movie_data.name)
        )
        return result.scalars().first()

    async def get_or_create_certification(self, name: str) -> CertificationModel:
        logger.info(f"Fetching or creating certification: {name}")
        result = await self.db.execute(select(CertificationModel).filter_by(name=name))
        certification = result.scalars().first()
        if not certification:
            logger.info(f"Creating new certification: {name}")
            certification = CertificationModel(name=name)
            self.db.add(certification)
            await self.db.commit()
            await self.db.refresh(certification)
        else:
            logger.info(f"Certification found: {certification.name}")

        return certification

    async def get_or_create_entities(self, model, names: list[str]) -> list[Any]:
        logger.info(f"Fetching or creating entities: {model}, {names}")
        objects = []
        for name in names:
            result = await self.db.execute(select(model).filter_by(name=name))
            entity = result.scalars().first()
            if not entity:
                logger.info(f"Creating new entity: {name}")
                entity = model(name=name)
                self.db.add(entity)
                await self.db.flush()
            else:
                logger.info(f"Entity found: {entity.name}")
            objects.append(entity)
        return objects

    async def create_movie_post(self, movie_data: MovieCreateSchema) -> MovieModel:
        logger.info(f"Creating new movie: {movie_data.name}")
        certification = await self.get_or_create_certification(
            movie_data.certifications
        )
        genres = await self.get_or_create_entities(GenreModel, movie_data.genres)
        stars = await self.get_or_create_entities(StarModel, movie_data.stars)
        directors = await self.get_or_create_entities(
            DirectorModel, movie_data.directors
        )

        movie = MovieModel(
            uuid=str(uuid4()),
            meta_score=movie_data.meta_score,
            gross=movie_data.gross,
            name=movie_data.name,
            year=movie_data.year,
            time=movie_data.time,
            imdb=movie_data.imdb,
            votes=movie_data.votes,
            price=movie_data.price,
            description=movie_data.description,
            certification_id=certification.id,
            genres=genres,
            stars=stars,
            directors=directors,
        )

        self.db.add(movie)
        await self.db.commit()
        await self.db.refresh(movie)

        result = await self.db.execute(
            select(MovieModel)
            .options(
                joinedload(MovieModel.certifications),
                joinedload(MovieModel.genres),
                joinedload(MovieModel.stars),
                joinedload(MovieModel.directors),
            )
            .filter(MovieModel.id == movie.id)
        )
        movie_with_relations = result.scalars().first()
        logger.info(f"Movie created: {movie_with_relations.name}")
        return movie_with_relations

    async def delete_instance(
        self, instance: Any
    ) -> Result[tuple[PurchasedModel]] | None:
        logger.info(f"Attempting to delete instance: {instance}")
        found_instance = await self.db.execute(
            select(func.count(PurchasedModel.id)).where(
                PurchasedModel.movie_id == instance.id
            )
        )
        if found_instance.scalar_one() > 0:
            logger.warning(
                f"Instance cannot be deleted, associated "
                f"purchases found: {found_instance.scalar_one()}"
            )
            return found_instance

        await self.db.delete(instance)
        await self.db.commit()
        logger.info(f"Instance deleted: {instance}")
        return None

    async def commit_instance(self, instance: Any) -> None:
        logger.info(f"Committing instance: {instance}")
        await self.db.commit()
        await self.db.refresh(instance)

    async def get_all_instances(self, instance: Any) -> list[Any]:
        logger.info(f"Retrieving instance: {instance}")
        result = await self.db.execute(select(instance))
        return result.scalars().all()

    async def get_or_create_model(self, instance: Any, name: str) -> tuple[Any, bool]:
        logger.info(f"Fetching or creating model: {name}")
        result = await self.db.execute(select(instance).filter_by(name=name))
        model = result.scalars().first()

        if model:
            return model, False
        logger.info(f"Creating new model: {name}")
        model = instance(name=name)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)

        return model, True

    async def get_instance_by_id(
        self, instance: Any, instance_id: int
    ) -> Optional[Any]:
        result = await self.db.execute(select(instance).filter_by(id=instance_id))
        return result.scalars().first()

    async def toggle_movie_like(
        self,
        movie: MovieModel,
        user_id: int,
    ) -> UserReactionModel:
        logger.info(f"Toggling like status for movie: {movie.name}, user_id: {user_id}")
        result = await self.db.execute(
            select(UserReactionModel).filter_by(movie_id=movie.id, user_id=user_id)
        )
        movie_like = result.scalars().first()
        if movie_like:
            movie_like.is_liked = not movie_like.is_liked
            movie_like.created_at = now()
        else:
            movie_like = UserReactionModel(
                user_id=user_id, movie_id=movie.id, is_liked=True
            )
            self.db.add(movie_like)

        await self.commit_instance(movie_like)
        logger.info(f"Movie like status toggled for movie: {movie.name}")
        return movie_like

    async def toggle_movie_favorite(
        self,
        movie: MovieModel,
        user_id: int,
    ) -> UserFavoriteModel:
        logger.info(f"Toggling favorite status for movie: {movie.name}, user_id: {user_id}")
        result = await self.db.execute(
            select(UserFavoriteModel).filter_by(movie_id=movie.id, user_id=user_id)
        )
        movie_fav = result.scalars().first()

        if movie_fav:
            movie_fav.is_favorite = not movie_fav.is_favorite
            movie_fav.created_at = now()
        else:
            movie_fav = UserFavoriteModel(
                user_id=user_id, movie_id=movie.id, is_favorite=True
            )
            self.db.add(movie_fav)

        await self.commit_instance(movie_fav)
        logger.info(f"Movie favorite status toggled for movie: {movie.name}")
        return movie_fav

    async def filter_movies(
        self,
        filters: dict[str, str],
        sort_by: Optional[MovieSortEnum] = None,
        user: UserModel = None,
    ) -> list[MovieModel]:
        logger.info(f"Filtering movies with filters: {filters}, sort_by: {sort_by}")
        if user:
            query = (
                select(MovieModel)
                .join(UserFavoriteModel)
                .filter(
                    UserFavoriteModel.user_id == user.id,
                    UserFavoriteModel.is_favorite is True,
                )
            )
        else:
            query = select(MovieModel)

        if filters.get("name"):
            query = query.filter(MovieModel.name.ilike(f"%{filters.get('name')}%"))
        if filters.get("search_person"):
            query = (
                query.join(MoviesStarsModel, isouter=True)
                .join(StarModel, isouter=True)
                .join(MoviesDirectorsModel, isouter=True)
                .join(DirectorModel, isouter=True)
                .filter(
                    or_(
                        StarModel.name.ilike(f"%{filters.get('search_person')}%"),
                        DirectorModel.name.ilike(f"%{filters.get('search_person')}%"),
                    )
                )
            )
        if filters.get("year") is not None:
            query = query.filter(MovieModel.year == filters["year"])
        if filters.get("min_imdb") is not None:
            query = query.filter(MovieModel.imdb >= float(filters["min_imdb"]))
        if filters.get("max_imdb") is not None:
            query = query.filter(MovieModel.imdb <= float(filters["max_imdb"]))
        if filters.get("min_price") is not None:
            query = query.filter(MovieModel.price >= float(filters["min_price"]))
        if filters.get("max_price") is not None:
            query = query.filter(MovieModel.price <= float(filters["max_price"]))

        if sort_by:
            if sort_by == MovieSortEnum.PRICE_ASC:
                query = query.order_by(MovieModel.price)
            elif sort_by == MovieSortEnum.PRICE_DESC:
                query = query.order_by(MovieModel.price.desc())
            elif sort_by == MovieSortEnum.RELEASE_YEAR_ASC:
                query = query.order_by(MovieModel.year)
            elif sort_by == MovieSortEnum.RELEASE_YEAR_DESC:
                query = query.order_by(MovieModel.year.desc())
            elif sort_by == MovieSortEnum.VOTES_ASC:
                query = query.order_by(MovieModel.votes)
            elif sort_by == MovieSortEnum.VOTES_DESC:
                query = query.order_by(MovieModel.votes.desc())
            elif sort_by == MovieSortEnum.IMDb_ASC:
                query = query.order_by(MovieModel.imdb)
            elif sort_by == MovieSortEnum.IMDb_DESC:
                query = query.order_by(MovieModel.imdb.desc())

        result = await self.db.execute(query)
        logger.info(f"Movies filtered, count: {len(result.scalars().all())}")
        return result.scalars().all()

    async def get_user_favorite_movies(self, user_id: int):
        logger.info(f"Fetching favorite movies for user_id: {user_id}")
        query = (
            select(MovieModel)
            .join(UserFavoriteModel)
            .filter(
                UserFavoriteModel.user_id == user_id,
                UserFavoriteModel.is_favorite is True,
            )
        )

        result = await self.db.execute(query)
        favorite_movies = result.scalars().all()
        logger.info(f"Favorite movies found: {len(favorite_movies)}")
        return favorite_movies
