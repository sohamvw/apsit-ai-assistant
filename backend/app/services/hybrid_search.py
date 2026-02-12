from app.services.vector_service import client, get_dense_embedding
from app.core.config import get_settings

settings = get_settings()


def hybrid_search(query: str, limit: int = 5):

    query_vector = get_dense_embedding(query)

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    documents = []

    for point in results.points:
        documents.append({
            "text": point.payload.get("text", ""),
            "url": point.payload.get("source", "")
        })

    return documents
