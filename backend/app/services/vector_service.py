from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from app.core.config import settings

print("Loading multilingual-e5-base embedding model...")

model = SentenceTransformer(
    settings.EMBEDDING_MODEL,
    device="cpu"
)

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
)


def embed_query(text: str):
    # E5 requires prefix
    text = f"query: {text}"

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        batch_size=8
    )

    return embedding.tolist()


def search_qdrant(query: str, top_k: int = 5):
    query_vector = embed_query(query)

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
    )

    return results
