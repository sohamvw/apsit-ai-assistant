from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "APSIT AI Assistant"
    ENV: str = "production"

    GEMINI_API_KEY: str

    QDRANT_URL:"https://924fafaa-e075-4a24-9b47-e84696b17d21.eu-west-1-0.aws.cloud.qdrant.io"
    QDRANT_API_KEY:"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.PLTloyBmI_Lybcv0DFhE-Lb_qa6Bjas6Vf_QrgFmQ0Y"
    QDRANT_COLLECTION: str = "apsit_knowledge"

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
