import psycopg
from psycopg.types.json import Jsonb
from typing import Optional

from cocoarag.dao.base import DAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.filters import FilterModel
from cocoarag.models.queries import QueryModel


class GetConversationHistoryDAO(DAO):
    def __call__(self,
                 conversation_id: str) -> list[Optional[dict|None]]:
        """ Get conversation history, return empty list
        if does not exist
        """
        select_conversation_sql = """
            SELECT content 
            FROM public.conversations
            WHERE conversation_id = %s;
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(select_conversation_sql, (conversation_id,))
                    history = cur.fetchall()
                    
                    if history:
                        return history[0][0]
                    else:
                        print(f"Conversation with ID {conversation_id} not found.")
                        return []
        except Exception as e:
            print(f"Error extracting document_id: {e}")


class SaveConversationHistoryDAO(DAO):
    def __call__(self,
                 user_id: str,
                 conversation_id: str,
                 content: dict) -> None:
        """ Save conversation into table 'conversations'.
        The query uses INSERT INTO ... ON CONFLICT (conversation_id) DO UPDATE, 
        which allows to add a new conversation and, if a conversation with that 
        conversation_id already exists, update the content field.

        Args:
            conversation_id (str): UUID conversation.
            user_id (str): UUID user.
            content (dict): Content wich will be saved as JSONB
        """
        insert_conversation_sql = """
        INSERT INTO public.conversations (conversation_id, user_id, content)
        VALUES (%s, %s, %s)
        ON CONFLICT (conversation_id) 
        DO UPDATE SET content = EXCLUDED.content;
        """

        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_conversation_sql,
                        (conversation_id, user_id, Jsonb(content))
                    )
                    conn.commit()
                    print(f"Conversation {conversation_id} saved successfully.")
        except Exception as e:
            print(f"Error saving conversation {conversation_id}: {e}")
            raise


class RewriteConversationHistoryDAO(DAO):
    def __call__(self,
                 conversation_history: list,
                 new_question:str,
                 new_answer:str,
                 num:int=10) -> list[dict]:
        """Keep last `num` questions and answers from conversation history.
        
        Args:
            conversation_history (list): The current conversation history, can be an empty list.
            new_question (str): The new user query to add.
            new_answer (str): The new model answer to add.
            num (int): Maximum number of question-answer pairs to keep. Default is 10.
        
        Returns:
            list[dict]: Updated conversation history with the latest `num` question-answer pairs.
        """
        conversation_history.append({"role": "user", "content": new_question})
        conversation_history.append({"role": "assistant", "content": new_answer})
        
        max_length = num * 2
        if len(conversation_history) > max_length:
            conversation_history = conversation_history[-max_length:]
        
        return conversation_history
    

# class SaveConversationHistoryDAO(DAO):
#     def __call__(self,
#                  user_id: str,
#                  conversation_id: str,
#                  content: dict) -> None:
#         """ Save new conversation into table 'conversations'. (conversation doesn't exist)
#         """
#         insert_conversation_sql = """
#         INSERT INTO public.conversations (conversation_id, user_id, content)
#         VALUES (%s, %s, %s)
#         """

#         try:
#             # Connect to the PostgreSQL database
#             with psycopg.connect(**self.connection_params) as conn:
#                 with conn.cursor() as cur:
#                     cur.execute(
#                         insert_conversation_sql,
#                         (conversation_id, user_id, Jsonb(content))
#                     )
#                     conn.commit()
#                     print(f"Conversation {conversation_id} saved successfully.")
#         except Exception as e:
#             print(f"Error saving conversation {conversation_id}: {e}")
#             raise


# class UpdateConversationHistoryDAO(DAO):
#     def __call__(self,
#                  user_id: str,
#                  conversation_id: str,
#                  content: dict) -> None:
#         """Update existing conversation (conversation already exists in the database)"""
#         update_conversation_sql = """
#         UPDATE public.conversations
#         SET content = %s
#         WHERE conversation_id = %s AND 
#               user_id = %s;
#         """

#         try:
#             # Connect to the PostgreSQL database
#             with psycopg.connect(**self.connection_params) as conn:
#                 with conn.cursor() as cur:
#                     cur.execute(
#                         update_conversation_sql,
#                         (Jsonb(content), conversation_id, user_id)
#                     )
#                     conn.commit()
#                     print(f"Conversation {conversation_id} updated successfully.")
#         except Exception as e:
#             print(f"Error updating conversation {conversation_id}: {e}")
#             raise


class AddUserDAO(DAO):
    def __call__(self,
                 user_id: str,
                 group_id:str,
                 username: str,
                 email: dict,
                 password: str,
                 metadata) -> None:
        """ Save new user into table 'users'."""
        insert_user_sql = """
        INSERT INTO public.users (user_id, group_id, username, email, password_hash, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_user_sql,
                        (
                            user_id, 
                            group_id,
                            username,
                            email,
                            password,
                            metadata
                        )
                    )
                    conn.commit()
                    print(f"User {username} saved successfully.")
        except Exception as e:
            print(f"Error saving User {username}: {e}")
            raise
    

# --------------------------- {} ---------------------------


class SimilaritySearchDAO(DAO):
    """ Extract chunk from vector store
    """
    def __call__(self,
                 query: QueryModel,
                 filter: FilterModel) -> list[ChunkModel]:
        # collection_name is a general collection name
        # from config
        vector_store = self.get_vector_store(
            self.config.quering.basic_collection_name
        )

        # scored_langchain_docs is [(Document, float), ...]
        scored_langchain_docs = vector_store.similarity_search_with_relevance_scores(
            query.content,
            k=self.config.quering.k,
            filter=filter.content, # Filter model
        )

        # print(langchain_docs)
        # print(vector_store.similarity_search_with_relevance_scores)
        # print(vector_store.similarity_search_with_relevance_scores.__doc__)
        # print(langchain_docs)
        # d = langchain_docs[0]
        # print(d)
        # print(d.__dir__())

        chunks = []
        for doc, score in scored_langchain_docs:
            chunk = ChunkModel(
                trace_id=query.trace_id,
                file_name=doc.metadata.get("filename", "Error"),
                content=doc.page_content.encode("utf-8"),
                metadata=doc.metadata,
                score=score
            )

            chunks.append(chunk)

        return chunks


if __name__ == "__main__":
    from uuid import uuid4

    str_query = "What happend to King?"
    query = QueryModel(
        trace_id=uuid4().hex,
        content=str_query
    )

    accessor = SimilaritySearchDAO()
    chunks = accessor(query=query, filters={})

    print(chunks)
