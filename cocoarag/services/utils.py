import re
import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


class CustomJSONParser(StrOutputParser):
    def parse(self, text: str) -> dict:
        # Regular expression to find JSON content within triple backticks
        json_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
        match = json_pattern.search(text)

        if match:
            json_str = match.group(1).strip()
            try:
                # Parse the JSON string into a dictionary
                json_obj = json.loads(json_str)
                return json_obj
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON content: {json_str}") from e
        else:
            raise ValueError("No JSON content found in the text")


def get_model(model_name: str) -> BaseChatModel:
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=2,  # 1 req every 500ms
        check_every_n_seconds=0.1  # check every 100ms
    )

    # Attention: I use highest API plan now
    rate_limiter = None

    match model_name:
        case "gpt-4o-mini":
            return ChatOpenAI(model=model_name, rate_limiter=rate_limiter)
        case "gpt-4o":
            return ChatOpenAI(model=model_name, rate_limiter=rate_limiter)
        case "gpt-3.5-turbo":
            return ChatOpenAI(model=model_name, rate_limiter=rate_limiter)

        case _:
            raise NotImplementedError(
                f"Model {model_name} not implemented."
                "You can add it by yourself, check utils.get_model"
            )
