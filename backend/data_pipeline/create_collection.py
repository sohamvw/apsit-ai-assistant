import json
import os
import time
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct,
    VectorParams,
    Distance
)

from google import genai
from google.genai import types

# =============================
# CONFIG
# =============================

GEMINI_API_KEY="AIzaSyCNXTNLtKLqOhZVy48WA83cjGOVb3bJGMc"
QDRANT_URL="https://18c5a0e7-8cd5-4930-8247-0752b0608513.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.FrldmN7Vk9SpEbgDFOTnXEuzozItJQTcfQ7L0mpXoxk"


COLLECTION_NAME = "apsit_knowledge"
DATA_FILE = "apsit_data.json"

VECTOR_SIZE = 3072
BATCH_SIZE = 20
PROGRESS_FILE = "ingestion_progress.json"

# =============================
# INIT
# =============================

print("🔄 Initializing Gemini client...")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

print("🔄 Connecting to Qdrant...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60,
)

# =============================
# CREATE COLLECTION IF NOT EXISTS
# =============================

collections = client.get_collections().collections
existing = [c.name for c in collections]

if COLLECTION_NAME not in existing:
    print("📦 Creating collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )
else:
    print("✅ Collection exists.")

# =============================
# LOAD DATA
# =============================

print("📂 Loading data...")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    documents = json.load(f)

total_docs = len(documents)
print(f"📄 Loaded {total_docs} documents")

# =============================
# LOAD PROGRESS
# =============================

if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress_data = json.load(f)
        start_index = progress_data.get("last_index", 0)
else:
    start_index = 0

print(f"🔁 Resuming from index: {start_index}")

# =============================
# EMBEDDING FUNCTION
# =============================

def embed_batch(texts):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    return [e.values for e in response.embeddings]

# =============================
# PROCESS ONE BATCH PER RUN
# =============================

if start_index >= total_docs:
    print("🎉 All documents already uploaded.")
    exit()

end_index = min(start_index + BATCH_SIZE, total_docs)
batch_docs = documents[start_index:end_index]

texts = []
clean_docs = []

for doc in batch_docs:
    text = doc.get("text", "").strip()
    if text:
        texts.append(text)
        clean_docs.append(doc)

print(f"🚀 Uploading batch from {start_index} to {end_index - 1}")

try:
    vectors = embed_batch(texts)

    points = []

    for doc, vector in zip(clean_docs, vectors):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "url": doc.get("url"),
                    "text": doc.get("text")[:3000]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print("✅ Batch uploaded successfully.")

    # Save progress
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_index": end_index}, f)

    print(f"💾 Progress saved. Next start index: {end_index}")

except Exception as e:
    print("❌ Error occurred:", e)
    print("⛔ Batch not marked complete.")
