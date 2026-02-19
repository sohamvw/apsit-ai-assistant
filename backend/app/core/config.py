from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "apsit_collection"

    # Embedding Model (E5)
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"

    # Gemini LLM (ONLY for answer generation)
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
