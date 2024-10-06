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