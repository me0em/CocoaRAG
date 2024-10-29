import fastapi

from pydantic import BaseModel

from cocoarag.models.documents import DocumentModel
from cocoarag.use_cases.documents import AddDocumentUseCase

router = fastapi.APIRouter(
    tags=["documents"],
    prefix="/documents"
)


class AddDocumentRequest(BaseModel):
    user_id: str
    user_group: str
    document: DocumentModel


@router.post("/add")
async def add_document(request: AddDocumentRequest):
    try:
        use_case = AddDocumentUseCase()
        use_case(
            user_id=request.user_id,
            user_group=request.user_group,
            document=request.document
        )
        return {"status": "success"}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
