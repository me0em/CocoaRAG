# document.py
import yaml
from uuid import uuid4
from box import Box

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

from cocoarag.models.documents import DocumentModel


def _load_config(path="../configs/credits.yml") -> Box:
    """ Load config and return it Box representation
    """
    with open(path, "r") as file:
        data: dict = yaml.safe_load(file)

    return Box(data)


config = _load_config()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=config.embeddings_model.open_ai.token
)

connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!


# TODO: maybe add_chunks_dao?
def add_documents_dao(documents: list[DocumentModel],
                      user_group: str):
    """ TODO
    """
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=user_group,
        connection=connection,
        use_jsonb=True,
    )

    docs = [
        Document(page_content=doc.content, metadata=doc.metadata)
        for doc in documents
    ]

    vector_store.add_documents(
        docs,
        ids=[doc.metadata["id"] for doc in docs]
    )

    return


if __name__ == "__main__":
    dummy_docs = [
        DocumentModel(
            content="The king is dead.".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="P3ty4",
            metadata={"id": uuid4().hex, "topic": "dummy"}
        ),
        DocumentModel(
            content="Long live the king!".encode('utf-8'),
            trace_id=uuid4().hex,
            file_name="P3ty4",
            metadata={"id": uuid4().hex, "topic": "dummy"}
        ),
    ]

    add_documents_dao(documents=dummy_docs, user_group="test")
