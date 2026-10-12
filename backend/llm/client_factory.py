from dotenv import load_dotenv
load_dotenv()
from backend.config.logger import logger
from backend.config.settings import settings

_PROVIDER = settings.LLM_PROVIDER.strip().lower()

if _PROVIDER == "groq":
    from backend.llm.groq_client import GroqLLM
    llm = GroqLLM()
    logger.info("LLM provider selected: Groq hosted inference.")
else:
    from backend.llm.ollama_client import OllamaLLM
    llm = OllamaLLM()
    logger.info("LLM provider selected: local Ollama.")