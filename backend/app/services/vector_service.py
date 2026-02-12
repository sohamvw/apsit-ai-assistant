from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def get_dense_embedding(text: str):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text
    )
    return response["embedding"]


def create_collection():
    client.recreate_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE,
        ),
        sparse_vectors_config={
            "bm25": SparseVectorParams()
        }
    )
