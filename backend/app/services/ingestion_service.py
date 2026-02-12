import uuid
from app.services.vector_service import client, get_dense_embedding
from app.services.crawler_service import crawl_site
from app.core.config import get_settings

settings = get_settings()


def run_ingestion():
    print("🚀 Starting ingestion...")

    documents = crawl_site("https://www.apsit.edu.in/")

    points = []

    for doc in documents:
        text = doc["text"]

        if not text or len(text) < 50:
            continue

        embedding = get_dense_embedding(text)

        points.append({
            "id": str(uuid.uuid4()),
            "vector": embedding,
            "payload": {
                "url": doc["url"],
                "text": text[:1000]
            }
        })

    if points:
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points
        )
        print(f"✅ Inserted {len(points)} documents into Qdrant")
    else:
        print("⚠️ No documents to insert")
