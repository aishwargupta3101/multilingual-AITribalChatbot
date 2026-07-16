from pathlib import Path

from backend.document_processing.pdf_loader import PDFLoader
from backend.document_processing.docx_loader import DOCXLoader
from backend.document_processing.txt_loader import TXTLoader

class DocumentLoader:

    @staticmethod
    def load(file_path: str):
        extension = (
            Path(file_path)
            .suffix
            .lower()
        )
        if extension == ".pdf":
            return PDFLoader.load(file_path)
        elif extension == ".docx":
            return DOCXLoader.load(file_path)
        elif extension == ".txt":
            return TXTLoader.load(file_path)
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

document_loader = DocumentLoader()