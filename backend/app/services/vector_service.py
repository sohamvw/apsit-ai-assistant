from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings

settings = get_settings()

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def get_dense_embedding(text: str):
    return embedding_model.encode(text, normalize_embeddings=True)


def create_collection():
    client.recreate_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=1024,
            distance=Distance.COSINE,
        ),
        sparse_vectors_config={
            "bm25": SparseVectorParams()
        }
    )
