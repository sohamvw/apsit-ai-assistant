import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

QDRANT_URL = os.environ["QDRANT_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

COLLECTION_NAME = "apsit-knowledge"

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def ensure_collection(vector_size: int):
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        print("[QDRANT] Collection created")

def ingest_documents(data_dir: str):
    texts = []

    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    texts.append(f.read())

    if not texts:
        print("[ERROR] No text files found")
        return

    print(f"[INFO] Loaded {len(texts)} documents")

    vectors = embedding_model.encode(texts)

    ensure_collection(vector_size=len(vectors[0]))

    points = []
    for text, vector in zip(texts, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={"text": text},
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print("[SUCCESS] Data uploaded to Qdrant")
