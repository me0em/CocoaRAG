# use_cases.py
from uuid import uuid4

from cocoarag.models.documents import DocumentModel
from cocoarag.services.documents import AddDocumentService


class AddDocumentAPIUseCase:
    def __call__(
        self,
        user_id: str,
        user_group: str,
        filename: str,
        metadata: dict,
        file_content: bytes,
    ) -> None:

        trace_id = uuid4().hex

        document = DocumentModel(
            trace_id=trace_id,
            file_name=filename,
            content=file_content,
            metadata=metadata,
        )

        service = AddDocumentService()
        service(user_id=user_id, user_group=user_group, document=document)
