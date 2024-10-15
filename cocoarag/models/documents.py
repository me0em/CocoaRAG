# models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID, uuid4


class DocumentModel(BaseModel):
    """ A model representing a document with a unique trace ID,
    filename, and raw content.

    Attributes:
        trace_id (UUID): A unique identifier for the document,
            representing a single user interaction.
        file_name (str): The name of the file.
        file_bytes (bytes): The raw content of the file.

    Methods:
        validate_file_size(v): Validates the size of the file content.
    """
    trace_id: UUID = Field(default_factory=uuid4,
                           frozen=True,
                           description="UUID represents a single user interaction")
    file_name: str = Field(description="Filename")
    content: bytes = Field(description="Raw content")
    metadata: dict

    @field_validator("content")
    @staticmethod
    def validate_file_size(v):
        min_size = 1  # 1 byte

        if len(v) < min_size:
            raise ValueError("File is too small. The minimum allowed file size is 512 bytes.")

        return v


class ChunkModel(DocumentModel):
    """ A model representing a chunk of a document.
    Inherits all attributes and methods from DocumentModel.
    """
    score: Optional[float]
