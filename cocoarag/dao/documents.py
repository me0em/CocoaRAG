# dao/document.py
from uuid import uuid4
from langchain_core.documents import Document
import psycopg

from cocoarag.models.documents import DocumentModel, ChunkModel
from cocoarag.dao.base import DAO


class AddChunksToVectorStoreDAO(DAO):
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 chunks: list[ChunkModel]) -> None:
        """Add chunks to the vector store.
        Use with `AddDocumentDAO` to have a
        relation: collection>document>chunks
        """
        # we create temporary id to use it in
        # collection name to use it instead of real uuid
        # (see "Attention!" below)
        mock_id = "mock_id_" + uuid4().hex
        vector_store = self.get_vector_store(collection_name=mock_id)

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

        # TODO:
        # GetRealCollectionIDDAO()
        # SELECT collection_id FROM ...

        # TODO:
        # AddToUserTableDocumentWithThisUUIDDAO()
        ...

        # ~~~ Attention! ~~~
        # Because of autism of Langchain developers,
        # we manually created tables for embeddings and
        # collections, emulated langchain behavior.
        # tables: `langchain_pg_collection` & `langchain_pg_embedding`
        #
        # But we expanded this tables, so we need to update
        # some of their values with raw SQL.

        accessor = UpdateCollectionInfoDAO()
        accessor(
            user_id=user_id,
            user_group=user_group,
            collection_name=mock_id
        )

        return


class UpdateCollectionInfoDAO(DAO):
    """ Update user_id and user_group
    in collection table to add documents
    and may be transfer ownership later
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 collection_name: str) -> None:
        # collection_name is mock_id

        # SQL command to insert data into the table
        update_data_sql = """
            UPDATE langchain_pg_collection
            SET user_id = %s, group_id = %s
            WHERE name = %s;
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_data_sql, (user_id, user_group, collection_name))
                    conn.commit()
                    print(f"Document updated successfully with id: {collection_name}")
        except Exception as e:
            print(f"Error inserting document: {e}")

        # ~~Attention!~~
        # We need a single collection_name for all documents
        # to query vector store correctly, so we
        # update collection_name after we use it to add
        # real document id to users table
        update_again_data_sql = """
            UPDATE langchain_pg_collection
            SET name = %s
            WHERE name = %s;
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        update_again_data_sql,
                        (
                            self.config.quering.basic_collection_name,
                            collection_name
                        )
                    )
                    conn.commit()
                    print("Document collection_name reupdated successfully")
        except Exception as e:
            print(f"Error inserting document: {e}")


class AddFileDAO(DAO):
    """ Add raw document with user and collection_id
        relations. Use with `AddChunksToVectorStoreDAO`
        to have a relation: user>document>chunks
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document: DocumentModel) -> None:
        # SQL command to insert data into the table
        insert_data_sql = """
        INSERT INTO files
        (user_id, collection_id, raw)
        VALUES (%s, %s, %s);
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_data_sql,
                                (user_id,
                                 document.metadata["id"],
                                 document.content))
                    conn.commit()
                    print(f"Document inserted successfully with id: {document.metadata['id']}")
        except Exception as e:
            print(f"Error inserting document: {e}")


class RemoveDocumentDAO(DAO):
    """ Remove document from langchain_pg_collection
    table which leads to removing all related chunks
    from langchain_pg_embedding
    """
    def __call__(self,
                 document_id: str) -> None:
        # SQL command to insert data into the table
        remove_data_sql = """
            DELETE FROM langchain_pg_collection
            WHERE uuid = %s;
        """
        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(remove_data_sql,
                                (document_id, ))
                    conn.commit()
                    print(f"Document removed successfully with id: {document_id}")
        except Exception as e:
            print(f"Error inserting document: {e}")


if __name__ == "__main__":

    accessor = RemoveDocumentDAO()
    accessor(document_id="5c921580-0a60-4240-ae24-0aac717bbbba")


    exit()


    filename = "King Arthur"
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
