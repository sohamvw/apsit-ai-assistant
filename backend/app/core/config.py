from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "APSIT AI Assistant"
    ENV: str = "production"

    GEMINI_API_KEY: str

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "apsit_knowledge"

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
