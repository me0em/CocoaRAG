<<<<<<< HEAD
from abc import ABC, abstractmethod
from typing import Optional, List

from cocoarag.models.documents import ChunkModel


class DocumentServiceInterface(ABC):

    @abstractmethod
    def add_document(self, user_group: str, document_id: str, title: str, document_metadata: Optional[str]) -> None:
        pass

    @abstractmethod
    def add_chunks(self, chunks: List[ChunkModel], user_group: str) -> None:
        pass


# from dao.documents import DocumentDAO
# from models.documents import DocumentModel
# # from langchain import LLMChain  # Assuming LangChain has an LLMChain class

# class DocumentService:
#     def __init__(self):
#         self.document_dao = DocumentDAO()
#         # self.llm_chain = LLMChain()  # Initialize your LangChain logic here

#     def add_document(self, id, content):
#         document_model = DocumentModel(id, content)

#         # TODO: split text
#         self.document_dao.add_document(document_model.document)
#         # TODO: add chunks

#     # def process_document(self, id, content):
#         # Example of using LangChain to process the document
#         # processed_content = self.llm_chain.process(content)
#         # return processed_content
=======
# documents.py
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from cocoarag.dao.documents import (
    AddChunksToVectorStoreDAO
)
from cocoarag.models.documents import (
    DocumentModel,
    ChunkModel
)


class SplitTextRecursivelyService:
    """ Wrapper around basic langchain splitter
    """
    def __init__(self,
                 chunk_size=200,
                 chunk_overlap=20,
                 length_function=len,
                 is_separator_regex=False):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            is_separator_regex=is_separator_regex
        )

    def __call__(self,
                 document: DocumentModel) -> list[ChunkModel]:
        texts = self.splitter.create_documents(
            [document.content.decode("utf-8")]
        )

        chunks = []
        for idx, text in enumerate(texts):
            chunk = ChunkModel(
                trace_id=document.trace_id,
                file_name=document.file_name,
                content=text.page_content.encode('utf-8'),
                metadata={
                    "id": f"{document.metadata['id']}::{idx}",
                    "topic": document.metadata['topic']
                }
            )

            chunks.append(chunk)

        return chunks


class AddDocumentService:
    """ Add document to the RAG system.

    Services called inside:
    - SplitTextRecursivelyService

    DAOs called inside:
    - AddDocumentToTableDAO
    - AddChunksToVectorStoreDAO
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document: DocumentModel) -> None:
        # split document content:
        service = SplitTextRecursivelyService()
        chunks: list[ChunkModel] = service(document)

        # insert chunks to the table
        accessor = AddChunksToVectorStoreDAO()
        accessor(
            user_id=user_id,
            user_group=user_group,
            chunks=chunks
        )


class RemoveDocumentService:
    """ Remove document from the RAG system.
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document_id: str) -> None:
        ...


if __name__ == "__main__":
    filepath = "../../dummy_files/bill-of-rights-analytics.txt"

    file_name = "Bill of Rights / Analytics"
    with open(filepath, "r") as file:
        document_text = file.read()
    document_id = uuid4().hex

    document = DocumentModel(
        trace_id=uuid4().hex,
        file_name=file_name,
        content=document_text,
        metadata={
            "id": document_id,
            "topic": "test"
        }
    )

    print("Document model has been created")

    # service = SplitTextRecursivelyService()
    # chunks = service(document)
    # print("Chunks has been created")
    # print(len(chunks))
    # print(chunks[-1])

    service = AddDocumentService()
    service(user_group="test", document=document)
>>>>>>> RemoveDocumentService
