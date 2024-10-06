import os
import yaml
from box import Box
from langchain.embeddings import OpenAIEmbeddings


class BaseService:
    def __init__(self, config_path="../configs/credits.yml"):
        self.config = self._load_config(config_path)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=self.config.embeddings_model.open_ai.token
        )
        self.connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
        self.connection_params = {
            "dbname": "langchain",
            "user": "langchain",
            "password": "langchain",
            "host": "localhost",
            "port": "6024"
        }

    def _load_config(self, path) -> Box:
        """Загружает конфигурацию и возвращает ее как объект Box."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, path)
        with open(config_path, "r") as file:
            data: dict = yaml.safe_load(file)
        return Box(data)
    




# class DocumentDAO:
#     def __init__(self, config_path="../configs/credits.yml"):
#         self.config = self._load_config(config_path)
#         self.embeddings = OpenAIEmbeddings(
#             model="text-embedding-3-small",
#             api_key=self.config.embeddings_model.open_ai.token
#         )
#         self.connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
#         self.connection_params = {
#             "dbname": "langchain",
#             "user": "langchain",
#             "password": "langchain",
#             "host": "localhost",
#             "port": "6024"
#         }

#     def _load_config(self, path) -> Box:
#         """Load config and return it as a Box representation."""
#         with open(path, "r") as file:
#             data: dict = yaml.safe_load(file)
#         return Box(data)

#     def add_chunks(self,
#                    chunks: list[ChunkModel],
#                    user_group: str) -> None:
#         """Add chunks to the vector store.
#         Use with `self.add_document` to have a
#         relation: collection>document>chunks
#         """
#         vector_store = PGVector(
#             embeddings=self.embeddings,
#             collection_name=user_group,
#             connection=self.connection,
#             use_jsonb=True,
#         )

#         langchain_docs = [
#             Document(page_content=chunk.content, metadata=chunk.metadata)
#             for chunk in chunks
#         ]

#         vector_store.add_documents(
#             langchain_docs,
#             ids=[doc.metadata["id"] for doc in langchain_docs]
#         )

#     def add_document(self,
#                      user_group: str,
#                      document_id: str,
#                      title: str,
#                      document_metadata: Optional[str]) -> None:
#         """ Add document to the database.
#         Use with `self.add_chunks` to have a
#         relation: collection>document>chunks
#         """

#         # SQL command to insert data into the table
#         insert_data_sql = """
#         INSERT INTO langchain_pg_document (id, collection_id, title, document_metadata)
#         VALUES (%s, %s, %s, %s);
#         """

#         try:
#             # Connect to the PostgreSQL database
#             with psycopg.connect(**self.connection_params) as conn:
#                 with conn.cursor() as cur:
#                     # Execute the SQL command to insert data into the table
#                     cur.execute(insert_data_sql, (document_id, user_group, title, document_metadata))
#                     conn.commit()
#                     print(f"Document inserted successfully with id: {id}")
#         except Exception as e:
#             print(f"Error inserting document: {e}")

















# def _load_config(path="../configs/credits.yml") -> Box:
#     """ Load config and return it Box representation
#     """
#     with open(path, "r") as file:
#         data: dict = yaml.safe_load(file)

#     return Box(data)


# config = _load_config()

# embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-small",
#     api_key=config.embeddings_model.open_ai.token
# )

# connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!



# # TODO: maybe add_chunks_dao?
# def add_documents_dao(documents: list[DocumentModel],
#                       user_group: str):
#     """ TODO
#     """
#     vector_store = PGVector(
#         embeddings=embeddings,
#         collection_name=user_group,
#         connection=connection,
#         use_jsonb=True,
#     )

#     docs = [
#         Document(page_content=doc.content, metadata=doc.metadata)
#         for doc in documents
#     ]

#     vector_store.add_documents(
#         docs,
#         ids=[doc.metadata["id"] for doc in docs]
#     )

#     return


# if __name__ == "__main__":
#     dummy_docs = [
#         DocumentModel(
#             content="The king is dead.".encode('utf-8'),
#             trace_id=uuid4().hex,
#             file_name="P3ty4",
#             metadata={"id": uuid4().hex, "topic": "dummy"}
#         ),
#         DocumentModel(
#             content="Long live the king!".encode('utf-8'),
#             trace_id=uuid4().hex,
#             file_name="P3ty4",
#             metadata={"id": uuid4().hex, "topic": "dummy"}
#         ),
#     ]

#     add_documents_dao(documents=dummy_docs, user_group="test")
