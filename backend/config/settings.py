from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_NAME : str ="Tribal AI Chatbot"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    MONGO_URI: str
    DATABASE_NAME: str
    LLAMA_MODEL: str
    VECTOR_DB_PATH: str
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
@lru_cache
def get_settings():
    return Settings()
settings = get_settings();