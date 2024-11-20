# models/filters.py
from pydantic import BaseModel, Field


class FiltersModel(BaseModel):
    """Represents a complex filter for similarity search"""

    # This Model expect filter to be using operators ($AND, $IN) only!!!!!
    content: dict[str, dict[str, list[str]]] | dict = Field(
        description="Filter logic for the query"
    )
