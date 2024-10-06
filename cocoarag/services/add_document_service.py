from services.documents import DocumentServiceInterface
from dao.documents import BaseService
from typing import Optional
import psycopg

class AddDocumentToPostgresService(DocumentServiceInterface, BaseService):
    def __init__(self, config_path="../configs/credits.yml"):
        BaseService.__init__(self, config_path)

    def add_document(self, user_group: str, document_id: str, title: str, document_metadata: Optional[str]) -> None:
        insert_data_sql = """
        INSERT INTO langchain_pg_document (id, collection_id, title, document_metadata)
        VALUES (%s, %s, %s, %s);
        """

        try:
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_data_sql, (document_id, user_group, title, document_metadata))
                    conn.commit()
                    print(f"Document inserted successfully with id: {document_id}")
        except Exception as e:
            print(f"Error inserting document: {e}")

    def add_chunks(self, chunks, user_group: str) -> None:
        """Метод не реализован, так как этот сервис не отвечает за добавление чанков."""
        raise NotImplementedError("This service does not implement add_chunks.")