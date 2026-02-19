from app.services.vector_service import search_qdrant


def hybrid_search(query: str):
    results = search_qdrant(query, top_k=5)

    documents = []

    for point in results:
        if point.score and point.score > 0.2:
            documents.append({
                "text": point.payload.get("text", ""),
                "url": point.payload.get("url", "")
            })

    return documents
