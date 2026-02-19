import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# 🔥 Updated collection + dimension
COLLECTION_NAME = "apsit_collection"
VECTOR_SIZE = 768


def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )


def create_collection_if_not_exists():
    client = get_qdrant_client()

    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        print(f"Creating collection '{COLLECTION_NAME}'...")

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print("Collection created.")

    # Ensure payload index exists for 'url'
    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="url",
            field_schema="keyword",
        )
        print("Payload index for 'url' ensured.")
    except Exception:
        pass


if __name__ == "__main__":
    create_collection_if_not_exists()
