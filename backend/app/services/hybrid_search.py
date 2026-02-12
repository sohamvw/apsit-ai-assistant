from app.services.vector_service import client, get_dense_embedding
from app.core.config import get_settings

settings = get_settings()


def hybrid_search(query: str, limit: int = 8):
    dense_vector = get_dense_embedding(query)

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=dense_vector,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )

    return [r.payload["text"] for r in results]
