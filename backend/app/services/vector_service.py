from qdrant_client import QdrantClient
from app.core.config import settings
import requests

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
)


def embed_query(text: str):
    """
    Instead of loading a local model,
    we call a lightweight embedding API.
    """

    response = requests.post(
        f"{settings.EMBEDDING_API_URL}",
        json={"text": f"query: {text}"},
        timeout=30,
    )

    response.raise_for_status()
    return response.json()["embedding"]


def search_qdrant(query: str, top_k: int = 5):
    query_vector = embed_query(query)

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
    )

    return results
