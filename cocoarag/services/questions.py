from uuid import uuid4
import yaml
import json
from box import Box

from langchain_core.messages import HumanMessage, SystemMessage

from cocoarag.services.utils import CustomJSONParser, get_model
from cocoarag.models.queries import QueryModel
from cocoarag.models.documents import ChunkModel


class GenerateQuestionService:
    def __init__(self, language="en"):
        with open("cocoarag/configs/prompts.yml", "r") as file:
            self.prompts: Box = Box(yaml.safe_load(file))

        self.model = get_model("gpt-4o-mini")

    def __call__(self,
                 chunks: list[ChunkModel],
                 language: str = "ru") -> QueryModel:
        """ Generate question based on provided chunks
        """
        texts = [
            chunk.content.decode("utf-8")
            for chunk in chunks
        ]

        system_prompt: str = self.prompts.question_generation.get(language)
        user_prompt: str = json.dumps(
            {"Facts": texts},
            ensure_ascii=False
        )

        parser = CustomJSONParser()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        chain = self.model | parser

        output = chain.invoke(messages)

        return output["facts"]


if __name__ == "__main__":
    from cocoarag.service.rag import GetSimilarChunksService

    user_id = "0755f33d-60c6-468d-884d-e49bc2c62fe6"
    user_group = "3e6edbaa-149f-4cfb-9958-b5ef648a9f63"
    query = "This query will "

    document_id = ...

    searcher = GetSimilarChunksService(
        user_id=user_id,
        group_id=user_group,
        query=QueryModel,
        filters=FiltersModel
    )

    chunks = GetSimilarChunksService()

    service = GenerateQuestionService()
    question: str = service()
