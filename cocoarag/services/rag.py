from typing import Any
from uuid import uuid4

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import RetrieveChunkModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.services.build_prompt import BuildContextualGenerationPromptService
from cocoarag.services.generate_answer import GenerateAnswerService


class GetSimilarChunksService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: Any = {}) -> list[RetrieveChunkModel]:
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
        """ Process user's query, retrieve relevant chunks, generate answer, and return AnswerModel 
        """
        service = GetSimilarChunksService()
        chunks: list[RetrieveChunkModel] = service(
            user_id=user_id,
            group_id=group_id,
            query=query,
            filters=filters
        )

        # TODO: understand how work RAG chain in
        # canonical one-line solutions and do the same
        # wrt our architecture

        if not chunks:
            return AnswerModel(
                trace_id=query.trace_id,
                content="Извините, я не нашел релевантной информации для вашего запроса.",
                # chunks=[]
            )

        prompt_service = BuildContextualGenerationPromptService()
        prompt = prompt_service(query, chunks)

        generation_service = GenerateAnswerService()
        generated_answer = generation_service(prompt)

        answer = AnswerModel(
            trace_id=query.trace_id,
            answer=generated_answer,
            # chunks=[]
        )

        return answer

if __name__ == "__main__":
    str_query = "What happend to King?"
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

    service = GetSimilarChunksService()
    chunks: list[RetrieveChunkModel] = service(
        user_id=uuid4().hex,
        group_id=uuid4().hex,
        query=query,
        filters={}
    )

    print('Chunks retrieved:', chunks, ' ', sep='\n')

    prompt_service = BuildContextualGenerationPromptService()
    prompt = prompt_service(query, chunks)
    print('Generated prompt:', prompt, ' ', sep='\n')

    generation_service = GenerateAnswerService()
    generated_answer = generation_service(prompt)
    print('RAG system answer:', generated_answer, ' ', sep='\n')

    print(query.trace_id, generated_answer.content)
    print(type(query.trace_id), type(generated_answer.content))

    answer = AnswerModel(
        trace_id=query.trace_id,
        content=generated_answer.content,
        # chunks=[]
    )
    print('RAG answer for user:', answer, ' ', sep='\n')
