from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from src.movies.schemas.examples.stars import star_schema_example


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [star_schema_example]},
    }


class StarCreateSchema(BaseModel):
    name: str


class StarsResponseSchema(BaseModel):
    stars: List[StarSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int

    model_config = ConfigDict(from_attributes=True)
