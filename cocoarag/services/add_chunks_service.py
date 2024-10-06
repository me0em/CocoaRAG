from typing import Optional
from services.documents import DocumentServiceInterface
from dao.documents import BaseService
from dao.docstore.document import Document
from langchain.vectorstores import PGVector
from cocoarag.models.documents import ChunkModel
from typing import List

class AddChunksToVectorDatabaseService(DocumentServiceInterface, BaseService):
    def __init__(self, config_path="../configs/credits.yml"):
        BaseService.__init__(self, config_path)

    def add_chunks(self, chunks: List[ChunkModel], user_group: str) -> None:
        vector_store = PGVector(
            embedding_function=self.embeddings,
            collection_name=user_group,
            connection_string=self.connection,
            use_json_field=True,
        )

        langchain_docs = [
            Document(page_content=chunk.content, metadata=chunk.metadata)
            for chunk in chunks
        ]

        vector_store.add_documents(
            langchain_docs,
            ids=[doc.metadata["id"] for doc in langchain_docs]
        )
        print("Chunks added successfully to the vector database.")

    def add_document(self, user_group: str, document_id: str, title: str, document_metadata: Optional[str]) -> None:
        """Метод не реализован, так как этот сервис не отвечает за добавление документов."""
        raise NotImplementedError("This service does not implement add_document.")
