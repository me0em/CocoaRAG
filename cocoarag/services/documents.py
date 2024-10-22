# documents.py
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from cocoarag.dao.documents import (
    AddChunksToVectorStoreDAO,
    UpdateCollectionInfoDAO,
    RemoveDocumentDAO
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
                    # document.metadata['id'] is not real document_id
                    "chunk_id": uuid4().hex,
                    "index": idx,
                    "filename": document.metadata['filename'],
                    "topic": document.metadata['topic'],
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
        document_id: str = accessor(
            user_id=user_id,
            user_group=user_group,
            chunks=chunks
        )

        print(f'AddDocumentService document_id: {document_id}')

        accessor = UpdateCollectionInfoDAO()
        accessor(
            user_id=user_id,
            user_group=user_group,
            content=document.content,
            new_document_name=document.file_name, # new 
            document_id=document_id
        )


class RemoveDocumentService:
    """ Remove document from the RAG system.
    """
    def __call__(self,
                 user_id: str,
                 user_group: str,
                 document_id: str) -> None:
        # delete document and all related embeddings
        accessor = RemoveDocumentDAO()
        accessor(
            document_id=document_id
        )


if __name__ == "__main__":
    import os 

    # filepath = "../../dummy_files/bill-of-rights-analytics.txt"
    filepath = "../../data/alice.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, filepath)
    config_path = os.path.normpath(config_path)

    # file_name = "Bill of Rights / Analytics"
    file_name = "Alice in Wonderland"

    with open(config_path, "r") as file:
        document_text = file.read()
    document_id = uuid4().hex

    user_id = uuid4().hex
    group_id = uuid4().hex
    print(f'User_id: {user_id}, Group_id:{group_id}')
    print(f'User downloaded the document: {file_name} service created id for it {document_id}')

    # document_id goes into metadata

    document = DocumentModel(
        trace_id=uuid4().hex,
        file_name=file_name,
        content=document_text,
        metadata={
            "filename": file_name,
            "id": document_id,
            "user_id": user_id,
            "topic": "test_alice"
        }
    )

    print("Document model has been created")

    service = AddDocumentService()
    service(
        user_id=user_id,
        user_group=group_id, 
        document=document
    )
    print('Document is in da house successfully')

    print('You have 10 seconds to check that ...')