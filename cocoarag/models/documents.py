# models.py
from entities.documents import Document

class DocumentModel:
    def __init__(self, id, content):
        self.document = Document(id=id, content=content)

    def to_dict(self):
        return self.document.dict()