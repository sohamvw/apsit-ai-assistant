import json
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct,
    VectorParams,
    Distance
)

from sentence_transformers import SentenceTransformer

# =============================
# CONFIG
# =============================

QDRANT_URL="https://18c5a0e7-8cd5-4930-8247-0752b0608513.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.FrldmN7Vk9SpEbgDFOTnXEuzozItJQTcfQ7L0mpXoxk"
COLLECTION_NAME = "apsit_knowledge"
DATA_FILE = "apsit_data.json"

VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output size
BATCH_SIZE = 20

# =============================
# INIT
# =============================

print("🔄 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔄 Connecting to Qdrant...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60,
)

# =============================
# CREATE COLLECTION (SAFE MODE)
# =============================

print("🔍 Checking collection...")

collections = client.get_collections().collections
existing = [c.name for c in collections]

if COLLECTION_NAME in existing:
    info = client.get_collection(COLLECTION_NAME)
    current_size = info.config.params.vectors.size

    if current_size != VECTOR_SIZE:
        print("⚠ Existing collection has wrong vector size.")
        print("🗑 Deleting old collection...")
        client.delete_collection(COLLECTION_NAME)

        print("📦 Creating new collection...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
    else:
        print("✅ Collection exists and is valid.")
else:
    print("📦 Creating collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

# =============================
# LOAD DATA
# =============================

print("📂 Loading data...")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"📄 Loaded {len(documents)} documents")

# =============================
# EMBED + PUSH
# =============================

points = []

for doc in documents:
    text = doc.get("text", "").strip()

    if not text:
        continue

    vector = model.encode(text).tolist()

    points.append(
        PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "url": doc.get("url"),
                "text": text[:2000]
            }
        )
    )

print(f"🚀 Uploading {len(points)} documents in batches...")

for i in range(0, len(points), BATCH_SIZE):
    batch = points[i:i + BATCH_SIZE]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=batch,
    )

    print(f"✅ Uploaded batch {i//BATCH_SIZE + 1}")

print("🎉 Upload complete!")
