from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_NAME : str ="Tribal AI Chatbot"
    APP_VERSION:str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    MONGODB_URI: str
    DATABASE_NAME: str
    LLAMA_MODEL: str
    MAX_NEW_TOKEN:int
    TEMPERATURE:float
    TOP_P:float
    VECTOR_DB_PATH: str
    EMBEDDING_MODEL:str
    NEMO_MODEL:str
    TRANSLATION_MODEL:str
    AWS_REGION:str
    AWS_BUCKET:str
    FRONTEND_URL:str
    CORS_ORIGINS:str
    LLM_PROVIDER: str = "groq"
    UPLOAD_DIR:str
    MAX_FILE_SIZE:int
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_MAX_TOKENS: int = 700
    GROQ_TEMPERATURE: float = 0.3
    GROQ_TIMEOUT_SECONDS: float = 180.0
    GROQ_TOP_P: float | None = None

    LLM_FALLBACK_TO_OLLAMA: bool = False

    # Optional Brave Search MCP integration (Groq/Gemini remains the LLM).
    WEB_SEARCH_ENABLED: bool = True
    BRAVE_SEARCH_API_KEY: str = ""
    POLLINATIONS_API_KEY: str = ""
    WEB_SEARCH_MCP_COMMAND: str = "npx"
    WEB_SEARCH_MCP_ARGS: str = '["-y", "@brave/brave-search-mcp-server"]'
    WEB_SEARCH_MAX_RESULTS: int = 5
    WEB_SEARCH_MAX_CONTEXT_CHARS: int = 6000
    ALLOWED_FILE_TYPES:str
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_PROXY_TOKEN: str = ""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    @property
    def cors_origins(self):
        return[
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")

        ]
@lru_cache
def get_settings():
    return Settings()
settings = get_settings();