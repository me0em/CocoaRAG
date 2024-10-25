# dao/document.py
import json
from langchain_core.documents import Document
import psycopg
from psycopg.types.json import Jsonb

from cocoarag.models.documents import DocumentModel, ChunkModel
from cocoarag.dao.base import DAO


class AddChunksToVectorStoreDAO(DAO):
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 chunks: list[ChunkModel]) -> None:
        """Add chunks to the vector store.
        Use with `AddDocumentRelationDAO` to have full information
        about parent document
        """
        vector_store = self.get_vector_store(
            collection_name=self.config.quering.basic_collection_name
        )

        langchain_docs = [
            Document(
                page_content=chunk.content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]

        vector_store.add_documents(
            langchain_docs,
            ids=[doc.metadata["chunk_id"] for doc in langchain_docs]
        )


class GetAllDocumentsByUserIDDAO(DAO):
    def __call__(self,
                 user_id: str) -> list[DocumentModel]:
        """ Get all documents by user id, in this
        function we return documents raw content too
        """
        get_documents_sql = f"""
            SELECT document_id, name, cmetadata FROM documents
            WHERE user_id = '{user_id}';
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(get_documents_sql)
                    documents = cur.fetchall()
                    print(f"{len(documents)} documents successfully extracted for {user_id}")
                    return documents
        except Exception as e:
            print(f"Error extracting document_id: {e}")


class AddDocumentRelationDAO(DAO):
    """ Add document id, name, content and metadata
        into dedicated table
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document: DocumentModel) -> None:
        # SQL command to insert data into the table
        insert_data_sql = """
        INSERT INTO documents
        (document_id, user_id, user_group, name, content, cmetadata)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        # try:
        if 1 == 1:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_data_sql,
                                (document.metadata["document_id"],
                                 user_id,
                                 user_group,
                                 document.file_name,
                                 document.content,
                                 Jsonb(document.metadata)))
                    conn.commit()
                    print(f"Document inserted successfully with id: {document.metadata['document_id']}")
        # except Exception as e:
            # print(f"Error inserting document: {e}")


class RemoveDocumentDAO(DAO):
    """ Remove document from documents & langchain_pg_collection
    """
    def __call__(self,
                 document_id: str) -> None:
        remove_from_documents_table_sql = f"""
            DELETE FROM documents
            WHERE document_id = '{document_id}';
        """

        jsonable_field = json.dumps({"document_id": document_id})
        remove_from_pg_embedding_sql = """
            DELETE FROM langchain_pg_embedding
            WHERE cmetadata @> '%s';
        """ % jsonable_field

        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(remove_from_documents_table_sql)
                    cur.execute(remove_from_pg_embedding_sql)
                    conn.commit()
                    print(f"Document removed successfully with id: {document_id}")
        except Exception as e:
            print(f"Error removing document: {e}")


if __name__ == "__main__":
    user_id = "d18ad67e-aa78-4bab-8e3f-1e50404b3c76"
    accessor = GetAllDocumentsByUserIDDAO()
    docs = accessor(user_id)
    print("===>>>", docs)
    """
    filename = "King Arthur (FROM DAO)"

    dummy_chunks = [
        ChunkModel(
            content="The king is dead.".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name=filename,  # useless
            metadata={
                "filename": filename,
                "topic": "dummy",
                "chunk_id": "id1",
            }
        ),
        ChunkModel(
            content="Long live the king!".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name=filename,  # useless
            metadata={
                "filename": filename,
                "topic": "dummy",
                "chunk_id": "id2",
            }
        ),
        ChunkModel(
            content="The king is fine".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name=filename,  # useless
            metadata={
                "filename": filename,
                "topic": "filter_check",
                "chunk_id": "id3",
            }
        ),
        ChunkModel(
            content="The king is a little bit sick".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name=filename,  # useless
            metadata={
                "filename": filename,
                "topic": "filter_check",
                "chunk_id": "id4",
            }
        ),
        ChunkModel(
            content="King will be okey next week!".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name=filename,  # useless
            metadata={
                "filename": filename,
                "topic": "filter_check",
                "chunk_id": "id5",
            }
        ),
    ]

    user_id = uuid4().hex

    print("A few chunks has been created")
    print(dummy_chunks)
    accessor = AddChunksToVectorStoreDAO()
    accessor(
        user_id=user_id,
        chunks=dummy_chunks,
        user_group=uuid4().hex
    )
    print("Insert chunks to the vector store")


    # dummy_document = DocumentModel(
    #     trace_id=uuid4().hex,
    #     file_name="p3ty4",
    #     content="The king is dead. Long live the king!".encode('utf-8'),
    #     metadata={"topic": "dummy"}
    # )

    # print("A dummy document has been created")
    # accessor = AddDocumentToTableDAO()
    # accessor(user_group="test", document=dummy_document)
    # print("Insert document to the database")
    """