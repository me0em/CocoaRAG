# dao/document.py
from typing import Optional, Any
import os
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
            model=self.config.embeddings_model.open_ai.embed_model,
            api_key=self.config.embeddings_model.open_ai.token
        )
        self.connection_string = self.config['database']['connection_string']
        self.connection_params = {
            "dbname": self.config['database']['dbname'],
            "user": self.config['database']['user'],
            "password": self.config['database']['password'],
            "host": self.config['database']['host'],
            "port": self.config['database']['port']
        }

    def _load_config(self, path) -> Box:
        """Load config and return it as a Box representation."""
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
    
    def get_connection(self):
        try:
            conn = psycopg.connect(**self.connection_params)
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def get_vector_store(self, collection_name: str):
        try:
            vector_store = PGVector(
                connection=self.connection_string,
                embeddings=self.embeddings,
                collection_name=collection_name,
                use_jsonb=True,
            )
            return vector_store
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def __call__(*args, **kwargs) -> Any: ...


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
            ids=[doc.metadata["id"] for doc in langchain_docs]
        )

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


# class AddDocumentToTableDAO(DAO):
#     """ Add document to the database.
#         Use with `AddChunksToVectorStoreDAO` to have a
#         relation: collection>document>chunks
#     """
#     def __call__(self,
#                  user_group: str,
#                  document: DocumentModel) -> None:
#         # SQL command to insert data into the table
#         insert_data_sql = """
#         INSERT INTO document
#         (id, collection_id, title, document_metadata)
#         VALUES (%s, %s, %s, %s);
#         """
#         try:
#             # Connect to the PostgreSQL database
#             with psycopg.connect(**self.connection_params) as conn:
#                 with conn.cursor() as cur:
#                     jsonable_metadata = json.dumps(document.metadata)
#                     cur.execute(insert_data_sql,
#                                 (document.metadata["id"],
#                                  user_group,
#                                  document.file_name,
#                                  jsonable_metadata))
#                     conn.commit()
#                     print(f"Document inserted successfully with id: {document.metadata['id']}")
#         except Exception as e:
#             print(f"Error inserting document: {e}")



if __name__ == "__main__":
    dummy_chunks = [
        ChunkModel(
            content="The king is dead.".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="XXX",
            metadata={"topic": "dummy2", "id": "x2"}
        ),
        ChunkModel(
            content="Long live the king!".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="XXX",
            metadata={"topic": "dummy2", "id": "x1"}
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

