import yaml
import json
from box import Box

from langchain_core.messages import HumanMessage, SystemMessage

from cocoarag.services.utils import CustomJSONParser, get_model
from cocoarag.models.queries import QueryModel


class GenerateQuestionService:
    def __init__(self, language="en"):
        with open("cocoarag/configs/prompts.yml", "r") as file:
            self.prompts: Box = Box(yaml.safe_load(file))

        self.model = get_model("gpt-4o-mini")

    def __call__(self,
                 facts: list[str],
                 language: str = "ru") -> QueryModel:
        """ Generate question based on provided chunks
        """

        system_prompt: str = self.prompts.question_generation.get(language)
        user_prompt: str = json.dumps(
            {"Facts": facts},
            ensure_ascii=False
        )

        parser = CustomJSONParser()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        chain = self.model | parser

        output = chain.invoke(messages)

        return output["question"]


if __name__ == "__main__":

    facts = [
        "Линкольн был выдающимся оратором.",
        "Речи Линкольна вдохновляли северян."
    ]

    service = GenerateQuestionService()
    question: str = service(facts=facts, language="ru")

    print(question)
