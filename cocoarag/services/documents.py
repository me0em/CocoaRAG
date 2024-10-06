# documents.py
from dao.documents import DocumentDAO
from models.documents import DocumentModel
# from langchain import LLMChain  # Assuming LangChain has an LLMChain class


class AddDocumentService:
    """ Add document to the RAG system.

    Services called inside:
    - SplitDocumentService

    TODO: ...
    """
    def __init__(self, document: DocumentModel) -> None:
        self.document = document

    def __call__(self):
        # split doc:
        ...

        # create chunks (with id logic):
        ...

        # insert doc to the table
        ...

        # insert chunks
        ...


class DocumentService:
    def __init__(self):
        self.document_dao = DocumentDAO()
        # self.llm_chain = LLMChain()  # Initialize your LangChain logic here

    def add_document(self, id, content):
        document_model = DocumentModel(id, content)

        # TODO: split text
        self.document_dao.add_document(document_model.document)
        # TODO: add chunks

    # def process_document(self, id, content):
        # Example of using LangChain to process the document
        # processed_content = self.llm_chain.process(content)
        # return processed_content
