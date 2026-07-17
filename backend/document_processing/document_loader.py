from pathlib import Path
from backend.document_processing.text_cleaner import text_cleaner
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
            text = PDFLoader.load(file_path)
        elif extension == ".docx":
            text = DOCXLoader.load(file_path)
        elif extension == ".txt":
            text = TXTLoader.load(file_path)
        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )
        text = text_cleaner.clean(text)
        return text

document_loader = DocumentLoader()