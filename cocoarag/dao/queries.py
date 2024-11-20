import psycopg
from psycopg.types.json import Jsonb
from typing import Optional

from cocoarag.dao.base import DAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.filters import FiltersModel
from cocoarag.models.queries import QueryModel


class GetConversationHistoryDAO(DAO):
    def __call__(self, conversation_id: str) -> list[Optional[dict | None]]:
        """Get conversation history, return empty list
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
                        return []
        except Exception as e:
            print(f"Error extracting document_id: {e}")


class SaveConversationHistoryDAO(DAO):
    def __call__(self, user_id: str, conversation_id: str, content: dict) -> None:
        """Save conversation into table 'conversations'.
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
                        (conversation_id, user_id, Jsonb(content)),
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error saving conversation {conversation_id}: {e}")
            raise


class SimilaritySearchDAO(DAO):
    """Extract chunk from vector store"""

    def __call__(
        self, query: QueryModel, filters: FiltersModel, k: Optional[int] = None
    ) -> list[ChunkModel]:
        # collection_name is a general collection name from config
        vector_store = self.get_vector_store(self.config.quering.basic_collection_name)

        if k is None:
            k = self.config.quering.k

        # scored_langchain_docs is [(Document, float), ...]
        scored_langchain_docs = vector_store.similarity_search_with_relevance_scores(
            query.content,
            k=self.config.quering.k,
            filter=filters.content,
        )

        chunks = []
        for doc, score in scored_langchain_docs:
            chunk = ChunkModel(
                trace_id=query.trace_id,
                file_name=doc.metadata.get("filename", "Error"),
                content=doc.page_content.encode("utf-8"),
                metadata=doc.metadata,
                score=score,
            )

            chunks.append(chunk)

        return chunks


if __name__ == "__main__":
    from uuid import uuid4

    str_query = "What happend to King?"
    query = QueryModel(trace_id=uuid4().hex, content=str_query)

    accessor = SimilaritySearchDAO()
    chunks = accessor(query=query, filters={})

    print(chunks)
