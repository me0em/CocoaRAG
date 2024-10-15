from langchain_core.documents import Document

from cocoarag.dao.base import DAO
from cocoarag.models.documents import ChunkModel
from cocoarag.models.query import QueryModel


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

        langchain_docs: list[Document] = vector_store.similarity_search(
            query.content,
            k=self.config.quering.k,
            filter=filters,
        )

        chunks = []
        for doc in langchain_docs:
            chunk = ChunkModel(
                trace_id=query.trace_id,
                file_name=doc.metadata.get("filename", "Error"),
                content=doc.page_content.encode("utf-8"),
                metadata=doc.metadata
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
