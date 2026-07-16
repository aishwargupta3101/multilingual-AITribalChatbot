from docx import Document

class DOCXLoader:
    @staticmethod
    def load(file_path:str):
        document = Document(file_path)
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text