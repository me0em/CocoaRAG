import os

import yaml
from box import Box

from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from langchain_openai import OpenAI


class ConversationService:
    """ TODO
    """
    def __init__(self,
                 config_path="../configs/credits.yml"):
        self.config = self._load_config(config_path)

        self.client = OpenAI(
            api_key=self.config.retrieve_model.open_ai.token
        )

        self.memory = ConversationSummaryBufferMemory(
            llm=self.client,
            max_token_limit=10
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
            self.memory.save_context({"input": "hi"}, {"output": "whats up"})
            self.memory.save_context({"input": "not much you"}, {"output": "not much"})
            self.memory.load_memory_variables({})
            


        except Exception as e:
            print(f"Error generating answer: {e}")
            raise



conversation_sum_mem = ConversationChain(
    llm=llm,
    memory=memory
)

# посмотрим как поменялся шаблон для промпта
print(conversation_sum_mem.memory.prompt.template)