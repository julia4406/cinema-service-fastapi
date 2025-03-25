from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GenreCreateSchema(BaseModel):
    name: str


class GenresResponseSchema(BaseModel):
    genres: List[GenreSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int

    model_config = ConfigDict(from_attributes=True)
