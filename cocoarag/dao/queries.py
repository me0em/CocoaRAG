import psycopg

from cocoarag.dao.base import DAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.filters import FilterModel
from cocoarag.models.queries import QueryModel


class GetHistoryDAO(DAO):
    def __call__(self,
                 conversation_id: str) -> list[dict]:
        """ Get conversation history, return empty list
        if does not exist
        """
        get_history_sql = f"""
            SELECT content FROM conversations
            WHERE conversation_id = '{conversation_id}';
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(get_history_sql)
                    history = cur.fetchall()
                    print(f"{len(history)} history successfully extracted; conversation_id={conversation_id}")
                    return history
        except Exception as e:
            print(f"Error extracting document_id: {e}")


class SaveHistoryDAO(DAO):
    def __call__(self,
                 user_id: str,
                 conversation_id: str,
                 content: dict,
                 is_new: bool) -> list[dict]:
        """ Save conversation history if is_new is True
        Otherwise update existing one
        """
        raw_content: bytes = content.encode("utf-8")

        if is_new:
            history_sql_query = """
                INSERT INTO conversations
                (conversation_id, user_id, content)
                VALUES (%s, %s, %b);
            """
            try:
                # Connect to the PostgreSQL database
                with psycopg.connect(**self.connection_params) as conn:
                    with conn.cursor() as cur:
                        cur.execute(history_sql_query,
                                    (conversation_id,
                                     user_id,
                                     raw_content))
                        conn.commit()
                        print(f"History inserted successfully with id: {conversation_id}")
            except Exception as e:
                print(f"Error inserting history: {e}")

        else:
            history_sql_query = """
                UPDATE conversations
                SET content = %b
                WHERE conversation_id = %s;
            """
            try:
                # Connect to the PostgreSQL database
                with psycopg.connect(**self.connection_params) as conn:
                    with conn.cursor() as cur:
                        cur.execute(history_sql_query,
                                    (raw_content,
                                     conversation_id))
                        conn.commit()
                        print(f"History inserted successfully with id: {conversation_id}")
            except Exception as e:
                print(f"Error inserting history: {e}")


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
