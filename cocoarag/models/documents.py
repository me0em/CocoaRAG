# models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID, uuid4


class DocumentModel(BaseModel):
    """A model representing a document with a unique trace ID,
    filename, and raw content.

    Attributes:
        trace_id (UUID): A unique identifier for the document,
            representing a single user interaction.
        file_name (str): The name of the file.
        file_bytes (bytes): The raw content of the file.

    Methods:
        validate_file_size(v): Validates the size of the file content.
    """

    trace_id: UUID = Field(
        default_factory=uuid4,
        frozen=True,
        description="UUID represents a single user interaction",
    )
    file_name: str = Field(description="Filename")
    content: bytes = Field(description="Raw content")
    metadata: dict  # TODO: validation & обязательные поля типа названия

    @field_validator("metadata")
    @staticmethod
    def validate_document_id_in_metadata(metadata):
        if "document_id" not in metadata:
            raise ValueError("document_id is missing in metadata")

        return metadata


class ChunkModel(DocumentModel):
    """A model representing a chunk of a document.
    Inherits all attributes and methods from DocumentModel.
    """

    pass


class RetrieveChunkModel(DocumentModel):
    """A model representing a chunk of a document.
    Inherits all attributes and methods from DocumentModel.
    """

    score: Optional[float] = None


if __name__ == "__main__":
    filename = "King Arthur"

    dummy_chunk_wo_score = ChunkModel(
        content="The king is dead.".encode("utf-8"),
        trace_id=uuid4().hex,
        file_name=filename,  # useless
        metadata={
            "filename": filename,
            "topic": "dummy",
            "chunk_id": "id1",
        },
    )

    dummy_chunk_with_score = ChunkModel(
        content="The king is dead.".encode("utf-8"),
        trace_id=uuid4().hex,
        file_name=filename,  # useless
        metadata={
            "filename": filename,
            "topic": "dummy",
            "chunk_id": "id1",
        },
        score=0.54,
    )
