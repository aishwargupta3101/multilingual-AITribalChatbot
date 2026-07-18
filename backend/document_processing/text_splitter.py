from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
class DocumentSplitter:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )
    def split(self, text:str,source:str="Unknown"):
        chunks = self.splitter.split_text(text)
        documents =[]
        for index,chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source":source,
                        "chunk":index +1
                    }
                )
            )
        return documents

document_splitter = DocumentSplitter()