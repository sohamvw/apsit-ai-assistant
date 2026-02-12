import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import qdrant_client

QDRANT_URL = os.environ["QDRANT_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

COLLECTION_NAME = "apsit-knowledge"

def ingest_documents(data_dir):
    print("[LOAD] Reading documents...")

    docs = SimpleDirectoryReader(
        data_dir,
        recursive=True,
        required_exts=[".txt", ".pdf"]
    ).load_data()

    print(f"[INFO] Documents loaded: {len(docs)}")

    client = qdrant_client.QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
    )

    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    print("[INDEX] Writing vectors to Qdrant...")
    VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    print(f"[SUCCESS] Stored in collection: {COLLECTION_NAME}")
