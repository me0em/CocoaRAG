# documents.py
from dao.documents import DocumentDAO
from models.documents import DocumentModel
# from langchain import LLMChain  # Assuming LangChain has an LLMChain class

class DocumentService:
    def __init__(self):
        self.document_dao = DocumentDAO()
        self.llm_chain = LLMChain()  # Initialize your LangChain logic here

    def add_document(self, id, content):
        document_model = DocumentModel(id, content)
        self.document_dao.add_document(document_model.document)

    def process_document(self, id, content):
        # Example of using LangChain to process the document
        processed_content = self.llm_chain.process(content)
        return processed_content
