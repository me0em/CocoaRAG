from typing import Any
from uuid import uuid4
import json

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.prompts.rag import rag_template_english_v0

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


class BuildContextualGenerationPromptService:
    def __call__(self,
                 query: QueryModel,
                 chunks: list[ChunkModel]) -> str:
        """ Build a contextual prompt for LLM generation
        using query and chunks
        """
        # context_payload is {"documents": [chunk1, chunk2]}
        context_payload = {"document": [chunk.content.decode("utf-8") for chunk in chunks]}
        context_payload = json.dumps(context_payload)

        prompt: str = rag_template_english_v0.format(
            context_payload=context_payload,
            user_query=query.content
        )

        prompt = prompt.strip()

        return prompt


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

        if not chunks:
            return AnswerModel(
                trace_id=query.trace_id,
                content="I didn't found any relevant documents",
            )

        prompt_service = BuildContextualGenerationPromptService()
        prompt = prompt_service(query, chunks)

        print(prompt)



if __name__ == "__main__":
    str_query = "What happend to King?"
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

    rag_service = QueryRAGSystemService()

    rag_service(
        user_id=uuid4().hex,
        group_id=uuid4().hex,
        query=query,
        filters={}
    )

    # service = GetSimilarChunksService()
    # chunks = service(
    #     user_id=uuid4().hex,
    #     group_id=uuid4().hex,
    #     query=query,
    #     filters={}
    # )

    # print(chunks)
