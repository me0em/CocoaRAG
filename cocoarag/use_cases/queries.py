from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.models.filters import FiltersModel
from cocoarag.services.rag import QueryRAGSystemService


class QueryRAGSystemAPIUseCase:
    def __call__(
        self,
        user_id: str,
        user_group: str,
        conversation_id: str,
        query: QueryModel,
        filters: FiltersModel,
    ) -> AnswerModel:
        service = QueryRAGSystemService()
        answer: AnswerModel = service(
            user_id, user_group, conversation_id, query, filters
        )

        return answer
