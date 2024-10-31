import json

from pydantic import BaseModel
import fastapi

from cocoarag.use_cases.conversations import (
    GetAllConversationsAPIUseCase,
    GetConversationAPIUseCase
)


router = fastapi.APIRouter(
    tags=["conversations"],
    prefix="/conversations"
)


class ConversationsList(BaseModel):
    conversations: list[str]


@router.post("/list")
async def list_converstions(
    user_id: str,
) -> ConversationsList:
    """ Return all conversation ids by user_id
    """
    try:
        ...

        conversations = ...

        return conversations

    except Exception as e:
        raise fastapi.HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/conversation")
async def get_converstions(
    conversation_id: str,
) -> str:
    """ Return conversation by conversation id as serialized json
    """
    try:
        ...

        conversation = ...

        return conversation

    except Exception as e:
        raise fastapi.HTTPException(
            status_code=500,
            detail=str(e)
        )
