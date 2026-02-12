from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

# ==============================
# CLIENTS
# ==============================

# Gemini client
genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Qdrant client
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# ==============================
# EMBEDDING
# ==============================

def get_dense_embedding(text: str):
    """
    Generate Gemini embedding (3072 dimensions)
    """
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    return response.embeddings[0].values


# ==============================
# COLLECTION SETUP
# ==============================

DOC_COLLECTION = settings.QDRANT_COLLECTION
STATE_COLLECTION = "apsit_ingestion_state"

VECTOR_SIZE = 3072


def create_collections():
    """
    Create collections only if they do not exist.
    Safe for production (does NOT wipe data).
    """

    existing_collections = [
        col.name for col in client.get_collections().collections
    ]

    # ---------------------------
    # Documents Collection
    # ---------------------------
    if DOC_COLLECTION not in existing_collections:
        client.create_collection(
            collection_name=DOC_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    # ---------------------------
    # Ingestion State Collection
    # ---------------------------
    if STATE_COLLECTION not in existing_collections:
        client.create_collection(
            collection_name=STATE_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
