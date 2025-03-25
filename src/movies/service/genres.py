from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.movies import GenreModel
from movies.repository.genres import GenresRepository
from movies.schemas.genres import GenreSchema, GenreCreateSchema


class GenresService:
    def __init__(self, db: AsyncSession):
        self.repository = GenresRepository(db)

    async def get_genres(
            self,
            page: int = 1,
            per_page: int = 10
    ):
        offset = (page - 1) * per_page
        genres = await self.repository.get_genres(limit=per_page, offset=offset)

        total_items = len(genres) or 0

        if not genres and total_items == 0:
            raise HTTPException(status_code=404, detail="No genres found.")

        total_pages = (total_items + per_page - 1) // per_page

        base_url = "/theater/genres/"
        prev_page_url = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
        next_page_url = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

        response_data = {
            "genres": genres,
            "prev_page": prev_page_url,
            "next_page": next_page_url,
            "total_pages": total_pages,
            "total_items": total_items
        }
        return response_data

    async def get_one_genre(self, genre_id: int):
        genre = await self.repository.get_genre(genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="No genre found.")

        return genre

    async def create_genre(self, genre: GenreCreateSchema):
        new_genre = GenreModel(
            name=genre.name,
        )

        created_genre = await self.repository.add_genre(new_genre)

        if created_genre is False:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"A genre with the name '{genre.name}' already exists."
                ),
            )
        try:
            return GenreSchema.model_validate(created_genre)

        except IntegrityError:
            raise HTTPException(status_code=400, detail="Invalid input data.")

    async def update_genre(self, genre_id: int, genre: GenreCreateSchema):
        result = await self.repository.update_genre(genre_id, genre)
        if result:
            return {"detail": "Genre updated successfully."}
        else:
            raise HTTPException(
                status_code=404, detail="Genre with the given ID was not found."
            )

    async def delete_genre(self, genre_id: int):
        result = await self.repository.delete_genre(genre_id)

        if result:
            return
        else:
            raise HTTPException(
                status_code=404,
                detail="Genre with the given ID was not found.",
            )
