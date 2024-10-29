# use_cases.py
from cocoarag.models.documents import DocumentModel
from cocoarag.services.documents import AddDocumentService


class AddDocumentUseCase:
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document: DocumentModel) -> None:
        service = AddDocumentService()
        service(
            user_id=user_id,
            user_group=user_group,
            document=document
        )
