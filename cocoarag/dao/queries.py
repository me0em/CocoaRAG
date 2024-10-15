from langchain_core.documents import Document

from cocoarag.dao.base import DAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.queries import QueryModel


class SimilaritySearchDAO(DAO):
    """ Extract chunk from vector store
    """
    def __call__(self,
                 query: QueryModel,
                 filters: dict) -> list[ChunkModel]:
        # collection_name is a general collection name
        # from config
        vector_store = self.get_vector_store(
            self.config.quering.basic_collection_name
        )

        # scored_langchain_docs is [(Document, float), ...]
        scored_langchain_docs = vector_store.similarity_search_with_relevance_scores(
            query.content,
            k=self.config.quering.k,
            filter=filters,
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
