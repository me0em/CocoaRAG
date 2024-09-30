# interfaces.py
from use_cases import AddDocumentUseCase, ProcessDocumentUseCase
from logging_config import log_info

class CLIInterface:
    def __init__(self):
        self.add_document_use_case = AddDocumentUseCase()
        self.process_document_use_case = ProcessDocumentUseCase()

    def add_document(self, id, content):
        log_info(f"Adding document with ID {id}")
        self.add_document_use_case.execute(id, content)

    def process_document(self, id, content):
        log_info(f"Processing document with ID {id}")
        processed_content = self.process_document_use_case.execute(id, content)
        print(f"Processed Content: {processed_content}")

if __name__ == "__main__":
    cli = CLIInterface()
    cli.add_document("doc1", "This is a sample document.")
    cli.process_document("doc1", "This is a sample document.")