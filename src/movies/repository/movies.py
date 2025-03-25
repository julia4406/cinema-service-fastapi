from typing import Optional, Any
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import func

from src.database.models.movies import (
    MovieModel,
    CertificationModel,
    DirectorModel,
    GenreModel,
    MovieModel,
    StarModel,
)
from src.movies.schemas.movies import MovieCreateSchema


class MoviesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_movies_paginated(
            self, page: int, per_page: int
    ) -> tuple[int, list[MovieModel]]:
        offset = (page - 1) * per_page

        total_items = await self.db.scalar(select(func.count()).select_from(MovieModel))

        query = (select(MovieModel)
            .order_by(MovieModel.id)
            .offset(offset).limit(per_page)
            .options(
                joinedload(MovieModel.genres),
                joinedload(MovieModel.stars),
                joinedload(MovieModel.directors),
                selectinload(MovieModel.certifications)
            )
        )
        result = await self.db.execute(query)
        movies = result.unique().scalars().all()

        return total_items, movies

    async def get_movie_by_id(self, movie_id: int) -> Optional[MovieModel]:
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

    async def get_detail_movies_by_id(
            self,
            movie_id: int
    ) -> Optional[MovieModel]:
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
            self,
            movie_data: MovieCreateSchema
    ) -> Optional[MovieModel]:
        result = await self.db.execute(
            select(MovieModel).filter(MovieModel.name == movie_data.name)
        )
        return result.scalars().first()

    async def get_or_create_certification(
            self,
            name: str
    ) -> CertificationModel:
        result = await self.db.execute(select(CertificationModel).filter_by(name=name))
        certification = result.scalars().first()
        if not certification:
            certification = CertificationModel(name=name)
            self.db.add(certification)
            await self.db.commit()
            await self.db.refresh(certification)

        return certification

    async def get_or_create_entities(
            self,
            model,
            names: list[str]
    ) -> list[Any]:
        objects = []
        for name in names:
            result = await self.db.execute(select(model).filter_by(name=name))
            entity = result.scalars().first()
            if not entity:
                entity = model(name=name)
                self.db.add(entity)
                await self.db.flush()
            objects.append(entity)
        return objects

    async def create_movie_post(
            self,
            movie_data: MovieCreateSchema
    ) -> MovieModel:
        certification = await self.get_or_create_certification(
            movie_data.certifications
        )
        genres = await self.get_or_create_entities(GenreModel, movie_data.genres)
        stars = await self.get_or_create_entities(StarModel, movie_data.stars)
        directors = await self.get_or_create_entities(
            DirectorModel,
            movie_data.directors
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

        return movie_with_relations

    async def delete_instance(self, instance: Any) -> None:
        await self.db.delete(instance)
        await self.db.commit()

    async def commit_instance(self, instance: Any) -> None:
        await self.db.commit()
        await self.db.refresh(instance)

    async def get_all_instances(self, instance: Any) -> list[Any]:
        result = await self.db.execute(select(instance))
        return result.scalars().all()

    async def get_or_create_model(
            self,
            instance: Any,
            name: str
    ) -> tuple[Any, bool]:
        result = await self.db.execute(select(instance).filter_by(name=name))
        model = result.scalars().first()

        if model:
            return model, False

        model = instance(name=name)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)

        return model, True

    async def get_instance_by_id(
            self,
            instance: Any,
            instance_id: int
    ) -> Optional[Any]:
        result = await self.db.execute(select(instance).filter_by(id=instance_id))
        return result.scalars().first()
