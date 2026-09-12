import os
from langchain_ollama import ChatOllama
from backend.config.settings import settings
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)
llm = ChatOllama(
    model=settings.LLAMA_MODEL,
    temperature=0.2,
    streaming=True,
    num_predict=settings.MAX_NEW_TOKEN,
    keep_alive="10m",
    base_url=OLLAMA_BASE_URL,
)