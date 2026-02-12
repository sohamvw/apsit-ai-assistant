from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from google import genai
from google.genai import types
from app.core.config import get_settings
import uuid

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
# Embedding
# -----------------------------
def get_embedding(text: str):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    return response.embeddings[0].values


# -----------------------------
# Create Collection If Not Exists
# -----------------------------
def create_collection():
    collections = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE,
            ),
        )


# -----------------------------
# Insert Document
# -----------------------------
def insert_document(text: str, url: str):
    vector = get_embedding(text)

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": text,
                    "url": url,
                },
            )
        ],
    )
