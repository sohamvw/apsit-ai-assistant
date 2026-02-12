import json
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

from google import genai
from google.genai import types


# =============================
# CONFIG
# =============================
GEMINI_API_KEY="AIzaSyDm7IX9Q2bOR4UfOwL6pTwDMKn36ra3D54"
QDRANT_URL="https://18c5a0e7-8cd5-4930-8247-0752b0608513.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.FrldmN7Vk9SpEbgDFOTnXEuzozItJQTcfQ7L0mpXoxk"


COLLECTION_NAME = "apsit_knowledge"
DATA_FILE = "apsit_data.json"


# =============================
# INIT CLIENTS
# =============================

genai_client = genai.Client(api_key=GEMINI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


# =============================
# EMBEDDING FUNCTION
# =============================

def get_embedding(text: str):
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",   # ✅ CORRECT MODEL
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )
    return response.embeddings[0].values


# =============================
# LOAD DATA
# =============================

with open(DATA_FILE, "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"📄 Loaded {len(documents)} documents")

points = []


# =============================
# CREATE VECTORS
# =============================

for doc in documents:
    text = doc.get("text", "").strip()

    if not text:
        continue

    vector = get_embedding(text)

    points.append(
        PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "url": doc.get("url"),
                "text": text[:2000],
            },
        )
    )

print(f"🚀 Uploading {len(points)} vectors...")

qdrant.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)

print("✅ Upload complete!")


