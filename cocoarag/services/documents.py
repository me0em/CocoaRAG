# documents.py
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from cocoarag.dao.documents import (
    AddChunksToVectorStoreDAO,
    AddDocumentRelationDAO,
    RemoveDocumentDAO,
)
from cocoarag.models.documents import DocumentModel, ChunkModel
from cocoarag.models.filters import FiltersModel
from cocoarag.models.queries import QueryModel
from cocoarag.services.facts import ExtractFactsService
from cocoarag.dao.queries import SimilaritySearchDAO


class GetAllDocumentChunksService:
    def __call__(self, document_id: str, trace_id: str) -> list[ChunkModel]:

        query = QueryModel(trace_id=trace_id, content="Any text here, k = 1e+6")

        filters = FiltersModel(content={"document_id": {"$in": [document_id]}})

        accessor = SimilaritySearchDAO()
        chunks = accessor(query=query, filters=filters, k=1e6)

        return chunks


class SplitTextRecursivelyService:
    """Wrapper around basic langchain splitter"""

    def __init__(
        self,
        chunk_size=200,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            is_separator_regex=is_separator_regex,
        )

    def __call__(self, document: DocumentModel) -> list[ChunkModel]:
        texts = self.splitter.create_documents([document.content.decode("utf-8")])

        chunks = []
        for idx, text in enumerate(texts):
            chunk = ChunkModel(
                trace_id=document.trace_id,
                file_name=document.file_name,
                content=text.page_content.encode("utf-8"),
                metadata={
                    "chunk_id": uuid4().hex,
                    "index": idx,
                    # document_id (relation on real document) is here
                    **document.metadata,
                },
            )

            chunks.append(chunk)

        return chunks


class AddDocumentService:
    """Add document to the RAG system.

    Services called inside:
    - SplitTextRecursivelyService

    DAOs called inside:
    - AddDocumentRelationDAO
    - AddChunksToVectorStoreDAO
    """

    def __call__(self, user_id: str, user_group: str, document: DocumentModel) -> None:
        # we need user_id in metadata to pass it in chunks
        # to filter relevant content
        if "user_id" not in document.metadata:
            document.metadata["user_id"] = user_id

        if "user_group" not in document.metadata:
            document.metadata["user_group"] = user_group

        # we do not use splitter here because we interpret facts as chunks

        extractor = ExtractFactsService()
        query = QueryModel(
            trace_id=document.trace_id, content=document.content.decode("utf-8")
        )
        raw_facts: list[str] = extractor(query)

        chunks: list[ChunkModel] = []
        for idx, raw_fact in enumerate(raw_facts):
            metadata = document.metadata
            metadata["chunk_id"] = str(idx)
            fact = ChunkModel(
                trace_id=document.trace_id,
                file_name=document.file_name,
                content=raw_fact.encode("utf-8"),
                metadata=metadata,
            )

            chunks.append(fact)

        # insert chunks to the table
        accessor = AddChunksToVectorStoreDAO()
        accessor(user_id=user_id, user_group=user_group, chunks=chunks)

        accessor = AddDocumentRelationDAO()
        accessor(user_id=user_id, user_group=user_group, document=document)


class RemoveDocumentService:
    """Remove document from the RAG system."""

    def __call__(self, document_id: str) -> None:
        # delete document and all related embeddings
        accessor = RemoveDocumentDAO()
        accessor(document_id=document_id)


if __name__ == "__main__":
    # file_name = "Linkoln"
    # raw = """Линкольн лично направлял военные действия, которые привели к победе над Конфедерацией во время Гражданской войны 1861—1865 годов. Его президентская деятельность привела к усилению исполнительной власти и отмене рабства на территории США. Линкольн включил в состав правительства ряд своих противников и смог привлечь их к работе над общей целью. Президент на всём протяжении войны удерживал Великобританию и другие европейские страны от интервенции. В его президентство построена трансконтинентальная железная дорога, принят Гомстед-акт, решивший аграрный вопрос. Линкольн был выдающимся оратором, его речи вдохновляли северян и являются ярким наследием до сих пор. По окончании войны предложил план умеренной Реконструкции, связанный с национальным согласием и отказом от мести. 14 апреля 1865 года Линкольн был смертельно ранен в театре, став первым убитым президентом США. Согласно общепринятой точке зрения и социальным опросам, он по-прежнему остаётся одним из лучших и самых любимых президентов Америки, хотя во время президентства подвергался суровой критике."""
    # document_id = uuid4().hex
    # user_id = uuid4().hex
    # group_id = uuid4().hex
    # print(f'User_id: {user_id}, Group_id:{group_id}')
    # print(f'User downloaded the document: {file_name} service created id for it {document_id}')

    # document = DocumentModel(
    #     trace_id=uuid4().hex,
    #     file_name=file_name,
    #     content=raw.encode("utf-8"),
    #     metadata={
    #         "filename": file_name,
    #         "document_id": document_id,
    #         "user_id": user_id,
    #         "topic": "paper"
    #     }
    # )

    # print(f"Document model has been created: {document.file_name}")

    # service = AddDocumentService()
    # service(
    #     user_id=user_id,
    #     user_group=group_id,
    #     document=document
    # )

    # print(f"Document has been added with id: {document.metadata['document_id']}")

    document_id = "3e6edbaa149f4cfb9958b5ef648a9f63"

    service = GetAllDocumentChunksService()
    chunks: list[ChunkModel] = service(document_id=document_id, trace_id=uuid4().hex)

    for chunk in chunks:
        print(f"• {chunk.content.decode('utf-8')}")
