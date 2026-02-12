from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

# Gemini client
genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Qdrant client
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
# Create Collection
# -----------------------------
def create_collection():
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE,
            ),
        )
        print("Collection created.")
    else:
        print("Collection already exists.")
