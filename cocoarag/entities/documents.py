# entities.py
from pydantic import BaseModel, Field, ValidationError

class Document(BaseModel):
    id: str = Field(..., description="The unique identifier for the document")
    content: str = Field(..., description="The content of the document")

    def validate(self):
        try:
            self.id = self.id.strip()
            self.content = self.content.strip()
            if not self.id:
                raise ValueError("Document ID is required.")
            if not self.content:
                raise ValueError("Document content is required.")
        except ValidationError as e:
            raise e
