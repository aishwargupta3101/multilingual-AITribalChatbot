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
    UPLOAD_DIR:str
    MAX_FILE_SIZE:int
    ALLOWED_FILE_TYPES:str
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