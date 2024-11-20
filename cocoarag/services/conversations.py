from typing import Optional
import os

import yaml
from box import Box

from cocoarag.dao.queries import GetConversationHistoryDAO, SaveConversationHistoryDAO


class GetConversaionHistoryService:
    def __call__(self, conversation_id: str) -> list[dict]:
        """Get conversation history, return empty list
        if does not exist
        """
        accessor = GetConversationHistoryDAO()
        history = accessor(conversation_id)

        return history


class SaveConversationHistoryService:
    def __init__(self, config_path="../configs/credits.yml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Box:
        """Load config and return it as a Box representation."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, self.config_path)
        config_path = os.path.normpath(config_path)
        try:
            with open(config_path, "r") as file:
                data: dict = yaml.safe_load(file)
            return Box(data)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            raise

    def trim_conversation(
        self,
        conversation_history: list[Optional[dict]],
        new_question: str,
        new_answer: str,
    ) -> list[Optional[dict]]:
        conversation_history.append({"role": "user", "content": new_question})
        conversation_history.append({"role": "assistant", "content": new_answer})

        return conversation_history[-2 * self.config.conversations.trim_limit :]

    def __call__(
        self,
        user_id: str,
        conversation_id: str,
        conversation_history: list[Optional[dict]],
        new_question: str,
        new_answer: str,
    ) -> None:
        """INSERT or UPDATE (if already exists) last `k`
        (Q, A) pairs to database (where k is a config value)
        """
        updated_conv_history = self.trim_conversation(
            conversation_history, new_question, new_answer
        )

        accessor = SaveConversationHistoryDAO()
        accessor(user_id, conversation_id, updated_conv_history)
