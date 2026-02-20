from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "apsit_collection"

    # LLM (Gemini)
    GEMINI_API_KEY: str

    # Embedding microservice (NEW)
    EMBEDDING_API_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
