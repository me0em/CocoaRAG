import json

import fastapi

from cocoarag.use_cases.documents import AddDocumentAPIUseCase


router = fastapi.APIRouter(tags=["documents"], prefix="/documents")


@router.post("/add")
async def add_document(
    user_id: str, user_group: str, file: fastapi.UploadFile, metadata: str
):
    print(metadata)

    try:
        content: bytes = await file.read()
        metadata: dict = json.loads(metadata)

        print(metadata)

        use_case = AddDocumentAPIUseCase()
        use_case(
            user_id=user_id,
            user_group=user_group,
            filename=file.filename,
            metadata=metadata,
            file_content=content,
        )
        return {"status": "success"}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
