import os

from langchain_ollama import ChatOllama
from backend.config.settings import settings


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)

OLLAMA_PROXY_TOKEN = os.getenv(
    "OLLAMA_PROXY_TOKEN",
    ""
)

client_kwargs = {}

if OLLAMA_PROXY_TOKEN:
    client_kwargs["headers"] = {
        "Authorization": f"Bearer {OLLAMA_PROXY_TOKEN}"
    }


llm = ChatOllama(
    model=settings.LLAMA_MODEL,
    temperature=0.2,
    streaming=True,
    num_predict=settings.MAX_NEW_TOKEN,
    keep_alive="10m",
    base_url=OLLAMA_BASE_URL,
    client_kwargs=client_kwargs,
)