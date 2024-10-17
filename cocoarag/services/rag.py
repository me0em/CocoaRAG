from typing import Any
import os
from uuid import uuid4
import json

import yaml
from box import Box
from openai import OpenAI

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.filters import FilterModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.prompts.rag import rag_template_english_v0


class GetSimilarChunksService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filter: FilterModel) -> list[ChunkModel]:
        """ Get relevant chunks with respect to user's query
        The amount of chunks (k) is a config value
        """
        accessor = SimilaritySearchDAO()
        chunks = accessor(query=query, filter=filter)

        return chunks


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


class QueryRAGSystemService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: FilterModel) -> AnswerModel:
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
        )

        return answer

if __name__ == "__main__":

    str_query = "What happend to King?"
    
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

    query_filter = {

    }

    filter = FilterModel(
        filter=query_filter
    )

    rag_service = QueryRAGSystemService()

    answer = rag_service(
        user_id=uuid4().hex,
        group_id=uuid4().hex,
        query=query,
        filters={}
    )

    print(answer)
