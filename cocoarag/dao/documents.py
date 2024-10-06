# dao/document.py
from typing import Optional, Any
import json
import yaml
from uuid import uuid4
from box import Box

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

import psycopg

from cocoarag.models.documents import DocumentModel, ChunkModel


class DAO:
    def __init__(self, config_path="../configs/credits.yml"):
        self.config = self._load_config(config_path)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.config.embeddings_model.open_ai.token
        )
        self.connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
        self.connection_params = {
            "dbname": "langchain",
            "user": "langchain",
            "password": "langchain",
            "host": "localhost",
            "port": "6024"
        }

    def _load_config(self, path) -> Box:
        """Load config and return it as a Box representation."""
        with open(path, "r") as file:
            data: dict = yaml.safe_load(file)
        return Box(data)

    def __call__(*args, **kwargs) -> Any: ...


class AddChunksToVectorStoreDAO(DAO):
    def __call__(self,
                 chunks: list[ChunkModel],
                 user_group: str) -> None:
        """Add chunks to the vector store.
        Use with `AddDocumentDAO` to have a
        relation: collection>document>chunks
        """
        vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=user_group,
            connection=self.connection,
            use_jsonb=True,
        )

        langchain_docs = [
            Document(
                page_content=chunk.content,
                metadata=chunk.metadata
            )
            for chunk in chunks
        ]

        vector_store.add_documents(
            langchain_docs,
            ids=[doc.metadata["id"] for doc in langchain_docs]
        )


class AddDocumentToTableDAO(DAO):
    """ Add document to the database.
        Use with `AddChunksToVectorStoreDAO` to have a
        relation: collection>document>chunks
    """
    def __call__(self,
                 user_group: str,
                 document: DocumentModel) -> None:
        # SQL command to insert data into the table
        insert_data_sql = """
        INSERT INTO document
        (id, collection_id, title, document_metadata)
        VALUES (%s, %s, %s, %s);
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    jsonable_metadata = json.dumps(document.metadata)
                    cur.execute(insert_data_sql,
                                (document.metadata["id"],
                                 user_group,
                                 document.file_name,
                                 jsonable_metadata))
                    conn.commit()
                    print(f"Document inserted successfully with id: {document.metadata['id']}")
        except Exception as e:
            print(f"Error inserting document: {e}")


if __name__ == "__main__":
    dummy_document = DocumentModel(
        trace_id=uuid4().hex,
        file_name="p3ty4",
        content="The king is dead. Long live the king!".encode('utf-8'),
        metadata={"id": "some-id", "topic": "dummy"}
    )

    print("A dummy document has been created")
    accessor = AddDocumentToTableDAO()
    accessor(user_group="test", document=dummy_document)
    print("Insert document to the database")

    dummy_chunks = [
        ChunkModel(
            content="The king is dead.".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="P3ty4",
            metadata={"id": uuid4().hex, "topic": "dummy"}
        ),
        ChunkModel(
            content="Long live the king!".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="P3ty4",
            metadata={"id": uuid4().hex, "topic": "dummy"}
        ),
    ]

    print("A few chunks has been created")
    print(dummy_chunks)
    accessor = AddChunksToVectorStoreDAO()
    accessor(chunks=dummy_chunks, user_group="test")
    print("Insert chunks to the vector store")
