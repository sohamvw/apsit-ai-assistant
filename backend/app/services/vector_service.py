from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

# -----------------------------
# Gemini Client
# -----------------------------
genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# -----------------------------
# Qdrant Client
# -----------------------------
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


# -----------------------------
# Embedding Function
# -----------------------------
def get_dense_embedding(text: str):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    return response.embeddings[0].values


# -----------------------------
# Create Collections (On Startup)
# -----------------------------
def create_collection():
    client.recreate_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE,
        ),
    )

    # State collection
    client.recreate_collection(
        collection_name="apsit_ingestion_state",
        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE,
        ),
    )
