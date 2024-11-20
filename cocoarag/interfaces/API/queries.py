import fastapi
from pydantic import BaseModel

from cocoarag.use_cases.queries import QueryRAGSystemAPIUseCase
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.models.filters import FiltersModel


router = fastapi.APIRouter(tags=["query"])


class QueryRequestModel(BaseModel):
    user_id: str
    user_group: str
    conversation_id: str
    query: QueryModel


@router.post("/query")
async def query_rag_system(request: QueryRequestModel) -> AnswerModel:
    """Query RAG system with different ids and text"""
    try:

        print(f">>> Get new query: {request.query.content}")

        filters = FiltersModel(content={})

        use_case = QueryRAGSystemAPIUseCase()
        answer: AnswerModel = use_case(
            user_id=request.user_id,
            user_group=request.user_group,
            conversation_id=request.conversation_id,
            query=request.query,
            filters=filters,
        )
        return answer

    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
