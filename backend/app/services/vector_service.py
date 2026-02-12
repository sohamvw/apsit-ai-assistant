from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
from google import genai
from app.core.config import get_settings

settings = get_settings()

# ----------------------------
# Gemini Client (Embeddings)
# ----------------------------
genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ----------------------------
# Qdrant Client
# ----------------------------
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# ----------------------------
# Dense Embedding Function
# ----------------------------
def get_dense_embedding(text: str):
    response = genai_client.models.embed_content(
        model="embedding-001",   # ✅ Correct & supported model
        contents=text
    )
    return response.embeddings[0].values


# ----------------------------
# Create / Recreate Collection
# ----------------------------
def create_collection():
    client.recreate_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=768,                 # ✅ embedding-001 = 768 dims
            distance=Distance.COSINE,
        ),
        sparse_vectors_config={
            "bm25": SparseVectorParams()
        }
    )
