# models/queries.py
from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4


class QueryModel(BaseModel):
    """A model representing a user query with a unique trace ID
    and string content.

    Attributes:
        trace_id (UUID): A unique identifier for the document,
            representing a single user interaction.
        content (str): User query

    Methods:
        validate_content_size(v): Validates the size of the query content.
    """

    trace_id: UUID = Field(
        default_factory=uuid4,
        frozen=True,
        description="UUID represents a single user interaction",
    )
    content: str = Field(description="User query")

    @field_validator("content")
    @staticmethod
    def validate_file_size(v):
        min_size = 1  # 1 byte

        if len(v) < min_size:
            raise ValueError("Query is too small.")

        return v


class AnswerModel(QueryModel):
    """Same as QueryModel, but
    used for storing model answers
    """

    pass
