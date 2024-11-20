from cocoarag.models.users import UserModel

import fastapi

from cocoarag.use_cases.users import AddUserAPIUseCase


router = fastapi.APIRouter(tags=["users"], prefix="/users")


@router.post("/add")
async def add_user(request: UserModel):
    try:
        use_case = AddUserAPIUseCase()
        use_case(request)
        return {"status": "success"}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
