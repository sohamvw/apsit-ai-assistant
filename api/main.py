import os
from fastapi import FastAPI
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import qdrant_client

# ---------------- ENV ----------------

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

COLLECTION_NAME = "apsit-knowledge"

# ---------------- APP ----------------

app = FastAPI(title="APSIT AI Assistant")

# ---------------- LLM ----------------

llm = Gemini(
    model="models/gemini-2.5-flash",
    api_key=GEMINI_API_KEY,
)

embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

Settings.llm = llm
Settings.embed_model = embed_model

# ---------------- VECTOR STORE ----------------

client = qdrant_client.QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
)

index = VectorStoreIndex.from_vector_store(vector_store)

query_engine = index.as_query_engine(
    similarity_top_k=5
)

# ---------------- SCHEMA ----------------

class QueryRequest(BaseModel):
    question: str

# ---------------- ROUTE ----------------

@app.post("/query")
async def query_bot(payload: QueryRequest):
    response = query_engine.query(payload.question)
    return {"answer": str(response)}
