# use_cases.py
from service.documents import DocumentService
from entities.documents import Document, ValidationError
from logging_config import log_info, log_error


class AddDocumentUseCase:
    def __init__(self):
        self.document_service = DocumentService()

    def execute(self, id, content):
        try:
            document = Document(id=id, content=content)
            document.validate()
            self.document_service.add_document(id, content)
            log_info(f"Document {id} added successfully.")
        except ValidationError as e:
            log_error(f"Validation error: {e}")
        except Exception as e:
            log_error(f"Error adding document: {e}")

class ProcessDocumentUseCase:
    def __init__(self):
        self.document_service = DocumentService()

    def execute(self, id, content):
        try:
            document = Document(id=id, content=content)
            document.validate()
            processed_content = self.document_service.process_document(id, content)
            log_info(f"Document {id} processed successfully.")
            return processed_content
        except ValidationError as e:
            log_error(f"Validation error: {e}")
        except Exception as e:
            log_error(f"Error processing document: {e}")