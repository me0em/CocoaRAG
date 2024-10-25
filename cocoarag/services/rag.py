from typing import Optional
import os
from uuid import uuid4
import json

import yaml
from box import Box
from openai import OpenAI

from cocoarag.dao.queries import SimilaritySearchDAO
from cocoarag.services.conversations import (
    GetConversaionHistoryService,
    SaveConversationHistoryService
)
from cocoarag.models.documents import ChunkModel
from cocoarag.models.filters import FiltersModel
from cocoarag.models.queries import QueryModel, AnswerModel
from cocoarag.prompts.rag import rag_template_english_v1


class GetSimilarChunksService:
    def __call__(self,
                 user_id: str,
                 group_id: str,
                 query: QueryModel,
                 filters: FiltersModel) -> list[ChunkModel]:
        """ Get relevant chunks with respect to user's query
        The amount of chunks (k) is a config value
        """
        accessor = SimilaritySearchDAO()
        chunks = accessor(query=query, filters=filters)

        return chunks


class BuildContexPromptService:
    def __call__(self,
                 history: list,
                 chunks: list[ChunkModel]) -> str:
        """ Build a contextual prompt for LLM generation chunks
        """
        formatted_history = []
        for message in history:
            if message['role'] == 'user':
                formatted_history.append(f"User Question: {message['content']}")
            elif message['role'] == 'assistant':
                formatted_history.append(f"Assistant Answer: {message['content']}")

        # Combine the formatted history into a single string
        conversation_history = "\n".join(formatted_history)

        # context_payload is {"documents": [chunk1, chunk2]}
        context_payload = {"document": [chunk.content.decode("utf-8") for chunk in chunks]}
        context_payload = json.dumps(context_payload)

        prompt: str = rag_template_english_v1.format(
            conversation_history=conversation_history,
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

    def __call__(self,
                 context_prompt: str,
                 user_prompt: str) -> str:
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
                 conversation_id: str,
                 query: QueryModel,
                 filters: FiltersModel) -> AnswerModel:
        """ Get user's query, process it and return answer
        """
        # TODO: history summary if it is necessary
        qa_service = GetConversaionHistoryService()
        qa_history: list[Optional[dict]] = qa_service(conversation_id)

        service = GetSimilarChunksService()

        if filters.content == {}:
            filters = FiltersModel(
                content={"user_id": {"$in": [user_id]}}
            )

        chunks: list[ChunkModel] = service(
            user_id=user_id,
            group_id=group_id,
            query=query,
            filters=filters
        )

        if not chunks:
            return AnswerModel(
                trace_id=query.trace_id,
                content="I didn't find any relevant documents",
            )

        prompt_service = BuildContexPromptService()
        context_prompt = prompt_service(qa_history, chunks)

        generation_service = GenerateAnswerService()
        generation_result: str = generation_service(
            context_prompt=context_prompt,
            user_prompt=query.content
        )

        answer = AnswerModel(
            trace_id=query.trace_id,
            content=generation_result,
        )

        save_conversation_service = SaveConversationHistoryService()
        save_conversation_service(
            user_id=user_id,
            conversation_id=conversation_id,
            conversation_history=qa_history,
            new_question=query.content,
            new_answer=generation_result
        )

        return answer


if __name__ == "__main__":
    from cocoarag.dao.queries import AddUserDAO
    from cocoarag.models.documents import DocumentModel
    from cocoarag.services.documents import AddDocumentService

    from cocoarag.dao.queries import SaveConversationHistoryDAO

    def create_new_user():
        user_id = uuid4().hex
        user_group = uuid4().hex

        add_user = AddUserDAO()
        add_user(
            user_id,
            user_group,
            f"test_user_{user_id}",
            f"test_user_{user_id}@example.com",
            "hashed_password",
            '{"role": "test"}'
        )

        return user_id, user_group
    
    def upload_document(user_id, group_id):
        import os

        filepath = "../../data/Story.txt"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, filepath)
        config_path = os.path.normpath(config_path)

        file_name = "Gay Fanfik"

        with open(config_path, "r") as file:
            document_text = file.read()

        document_id = uuid4().hex

        document = DocumentModel(
            trace_id=uuid4().hex,
            file_name=file_name,
            content=document_text,
            metadata={
                "filename": file_name,
                "document_id": document_id,
                "user_id": user_id,
                "topic": "test",
                "location": "London"
            }
        )

        service = AddDocumentService()
        service(
            user_id=user_id,
            user_group=group_id,
            document=document
        )

    def save_conversation_info(user_id, conversation_id):
        history = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": "What is the population of Paris?"},
            {"role": "assistant", "content": "The population of Paris is \
             around 2.1 million."}
        ]

        save_conversation_service = SaveConversationHistoryDAO()
        save_conversation_service(user_id, conversation_id, history)

    def check_conversations_work():
        print("======Creating new User========")
        user_id, user_group = create_new_user()
        print(f'User : {user_id} created')

        print("======Creating document and chunks for retriever========")
        upload_document(user_id, user_group)
        print(f'Documents for User {user_id} saved')

        print("======Saving conversation into bd========")
        conversation_id = uuid4().hex
        save_conversation_info(user_id, conversation_id)
        print(f'Conversation {conversation_id} for User {user_id} uploaded')

        print("======Answer with already existing conversation ========")

        query = QueryModel(
            trace_id=uuid4().hex,
            content="What is the name of Petya friend? And population in Paris?"
        )
        filters = FiltersModel(
            content={}
        )
        rag_query = QueryRAGSystemService()
        answer = rag_query(
            user_id, user_group, conversation_id, query, filters
        )

        print(answer)

    def pizdezh():
        user_id, user_group = create_new_user()
        print(f"Create user: {user_id}")
        upload_document(user_id, user_group)
        print("Document has been uploaded")
        conversation_id = uuid4().hex

        try:
            "📖 Conversation started. To interrupt press Control+C"
            while True:
                raw_query = input("🧐 Question: ")
                query = QueryModel(trace_id=uuid4().hex, content=raw_query)
                filters = FiltersModel(content={})
                rag_query = QueryRAGSystemService()
                answer = rag_query(
                    user_id,
                    user_group,
                    conversation_id,
                    query,
                    filters
                )
                print(f"🤖 AI: {answer.content}")

        except KeyboardInterrupt:
            print("\n\n💀 Conversation has been interrupted by user\n\n")

    # check_conversations_work()

    pizdezh()
