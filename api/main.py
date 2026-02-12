import os
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# ---------------- ENV ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("Missing QDRANT credentials")

genai.configure(api_key=GEMINI_API_KEY)

# ---------------- INIT ----------------

app = FastAPI(title="APSIT AI Assistant")

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

COLLECTION_NAME = "apsit-knowledge"

gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- SCHEMA ----------------

class QueryRequest(BaseModel):
    question: str

# ---------------- SEARCH ----------------

def search_qdrant(query: str, limit: int = 5):
    vector = embedding_model.encode(query).tolist()

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit,
    )

    texts = []
    for r in results:
        if "text" in r.payload:
            texts.append(r.payload["text"])

    return "\n\n".join(texts)

# ---------------- ROUTE ----------------

@app.post("/query")
async def query_bot(payload: QueryRequest):

    context = search_qdrant(payload.question)

    if not context:
        return {"answer": "No relevant information found."}

    prompt = f"""
You are the official APSIT AI assistant.
Answer strictly based on the context below.

Context:
{context}

Question:
{payload.question}

Answer clearly and concisely.
"""

    response = gemini_model.generate_content(prompt)

    return {"answer": response.text}
