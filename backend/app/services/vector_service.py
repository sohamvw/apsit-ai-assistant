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

COLLECTION_NAME = settings.QDRANT_COLLECTION


# -----------------------------
# Embedding Function
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
# Create Collection (SAFE)
# -----------------------------
def create_collection():
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE,
            ),
        )
        print("Collection created.")
    else:
        print("Collection already exists.")

# Insert Document
# -----------------------------
def insert_document(text: str, source: str):
    embedding = get_embedding(text)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "source": source
                },
            )
        ],
    )

