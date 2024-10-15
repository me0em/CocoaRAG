from typing import Any
from uuid import uuid4

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.queries import QueryModel, AnswerModel


class GetSimilarChunksService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: Any = {}) -> list[ChunkModel]:
        """ Get relevant chunks with respect to user's query
        The amount of chunks (k) is a config value
        """
        accessor = SimilaritySearchDAO()
        chunks = accessor(query=query, filters=filters)

        return chunks


class QueryRAGSystemService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: Any = {}) -> AnswerModel:
        """ Get user's query, process it and return answer
        """
        service = GetSimilarChunksService()
        chunks: list[ChunkModel] = service(
            user_id=user_id,
            group_id=group_id,
            query=query,
            filters=filters
        )


if __name__ == "__main__":
    str_query = "What happend to King?"
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

    service = GetSimilarChunksService()
    chunks = service(
        user_id=uuid4().hex,
        group_id=uuid4().hex,
        query=query,
        filters={}
    )

    print(chunks)

    # print("========")

    # print(chunks[0].metadata)

    # print("========")