import os

from langchain_ollama import ChatOllama
from backend.config.settings import settings
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434"
)
llm = ChatOllama(
    model=settings.LLAMA_MODEL,
    temperature=settings.TEMPERATURE,
    streaming=True,
    num_predict=settings.MAX_NEW_TOKEN,
    base_url=OLLAMA_BASE_URL,
)