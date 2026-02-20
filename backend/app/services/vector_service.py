from qdrant_client import QdrantClient
from app.core.config import settings
import requests


client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
)


def embed_query(text: str):
    response = requests.post(
        f"{settings.EMBEDDING_API_URL}/embed",
        json={"texts": [text]},
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    embedding = data["embeddings"][0]

    print("\n=== EMBEDDING DEBUG ===")
    print("Query:", text)
    print("Embedding length:", len(embedding))
    print("=======================\n")

    return embedding


def search_qdrant(query: str, top_k: int = 5):
    query_vector = embed_query(query)

    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    print("\n=== QDRANT DEBUG ===")
    print("Top K:", top_k)
    print("Number of points returned:", len(response.points))

    for idx, point in enumerate(response.points):
        print(f"\nResult {idx + 1}")
        print("Score:", point.score)
        print("Payload text preview:",
              point.payload.get("text", "")[:200])
        print("URL:", point.payload.get("url"))

    print("=====================\n")

    return response.points
