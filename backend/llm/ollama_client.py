from langchain_ollama import ChatOllama
from backend.config.settings import settings

llm = ChatOllama(
    model=settings.LLAMA_MODEL,
    temperature=settings.TEMPERATURE,
    streaming=True,
    num_predict=settings.MAX_NEW_TOKEN,
)
