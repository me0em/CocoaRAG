from typing import Any
<<<<<<< HEAD
from uuid import uuid4

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import RetrieveChunkModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.services.build_prompt import BuildContextualGenerationPromptService
from cocoarag.services.generate_answer import GenerateAnswerService
=======
import os
from uuid import uuid4
import json

import yaml
from box import Box
from openai import OpenAI

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.prompts.rag import rag_template_english_v0
>>>>>>> RemoveDocumentService


class GetSimilarChunksService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
<<<<<<< HEAD
                 filters: Any = {}) -> list[RetrieveChunkModel]:
=======
                 filters: Any = {}) -> list[ChunkModel]:
>>>>>>> RemoveDocumentService
        """ Get relevant chunks with respect to user's query
        The amount of chunks (k) is a config value
        """
        accessor = SimilaritySearchDAO()
        chunks = accessor(query=query, filters=filters)

        return chunks


<<<<<<< HEAD
=======
class BuildContexPromptService:
    def __call__(self,
                 chunks: list[ChunkModel]) -> str:
        """ Build a contextual prompt for LLM generation chunks
        """
        # context_payload is {"documents": [chunk1, chunk2]}
        context_payload = {"document": [chunk.content.decode("utf-8") for chunk in chunks]}
        context_payload = json.dumps(context_payload)

        prompt: str = rag_template_english_v0.format(
            context_payload=context_payload
        )

        prompt = prompt.strip()

        return prompt


class GenerateAnswerService:
    """ Service to generate an answer using
    an LLM based on the provided prompt
    """
    def __init__(self,
                 config_path="../configs/credits.yml"):
        self.config = self._load_config(config_path)

        self.client = OpenAI(
            api_key=self.config.retrieve_model.open_ai.token
        )

    def _load_config(self, path: str) -> Box:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, path)
        config_path = os.path.normpath(config_path)
        try:
            with open(config_path, "r") as file:
                data: dict = yaml.safe_load(file)
            return Box(data)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            raise

    def __call__(self, context_prompt: str, user_prompt: str) -> str:
        """ Generates an answer based on the given prompt.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.retrieve_model.open_ai.model,
                messages=[
                    {
                        "role": "system",
                        "content": context_prompt
                    },
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=512,
                n=1,
                stop=None,
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            return answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise


>>>>>>> RemoveDocumentService
class QueryRAGSystemService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: Any = {}) -> AnswerModel:
<<<<<<< HEAD
        """ Process user's query, retrieve relevant chunks, generate answer, and return AnswerModel 
        """
        service = GetSimilarChunksService()
        chunks: list[RetrieveChunkModel] = service(
=======
        """ Get user's query, process it and return answer
        """
        service = GetSimilarChunksService()
        chunks: list[ChunkModel] = service(
>>>>>>> RemoveDocumentService
            user_id=user_id,
            group_id=group_id,
            query=query,
            filters=filters
        )

<<<<<<< HEAD
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
=======
        if not chunks:
            return AnswerModel(
                trace_id=query.trace_id,
                content="I didn't found any relevant documents",
            )

        prompt_service = BuildContexPromptService()
        context_prompt = prompt_service(chunks)

        print("==============")
        print(context_prompt)
        print("==============")
        print(query.content)
        print("==============")

        generation_service = GenerateAnswerService()
        generation_result: str = generation_service(
            context_prompt=context_prompt,
            user_prompt=query.content
        )

        answer = AnswerModel(
            trace_id=query.trace_id,
            content=generation_result,
>>>>>>> RemoveDocumentService
        )

        return answer

<<<<<<< HEAD
=======

>>>>>>> RemoveDocumentService
if __name__ == "__main__":
    str_query = "What happend to King?"
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

<<<<<<< HEAD
    service = GetSimilarChunksService()
    chunks: list[RetrieveChunkModel] = service(
=======
    rag_service = QueryRAGSystemService()

    answer = rag_service(
>>>>>>> RemoveDocumentService
        user_id=uuid4().hex,
        group_id=uuid4().hex,
        query=query,
        filters={}
    )

<<<<<<< HEAD
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
=======
    print(answer)
>>>>>>> RemoveDocumentService
