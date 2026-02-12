import uuid
from datetime import datetime
from qdrant_client.models import PointStruct
from app.services.vector_service import client, get_dense_embedding
from app.core.config import get_settings
from .crawler_service import crawl
from .file_extractors import *

settings = get_settings()

DOC_COLLECTION = settings.QDRANT_COLLECTION
STATE_COLLECTION = "apsit_ingestion_state"


# -----------------------------
# Save Ingestion State
# -----------------------------
def save_state(run_id, payload):
    client.upsert(
        collection_name=STATE_COLLECTION,
        points=[
            PointStruct(
                id=run_id,
                vector=[0.0] * 3072,
                payload=payload
            )
        ]
    )


# -----------------------------
# Main Ingestion
# -----------------------------
def run_ingestion():
    run_id = str(uuid.uuid4())
    processed = []

    save_state(run_id, {
        "status": "running",
        "processed_urls": [],
        "started_at": str(datetime.utcnow())
    })

    for url, content_type, content in crawl("https://www.apsit.edu.in/"):

        text = ""

        if "text/html" in content_type:
            text = extract_html(url)
        elif "pdf" in content_type:
            text = extract_pdf(content)
        elif "word" in content_type:
            text = extract_docx(content)
        elif "sheet" in content_type:
            text = extract_xlsx(content)
        elif "presentation" in content_type:
            text = extract_pptx(content)

        if not text or not text.strip():
            continue

        # Chunking
        chunks = [text[i:i + 800] for i in range(0, len(text), 800)]

        for chunk in chunks:
            embedding = get_dense_embedding(chunk)

            client.upsert(
                collection_name=DOC_COLLECTION,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": chunk,   # 🔥 FIXED (was "chunk")
                            "url": url,
                            "timestamp": str(datetime.utcnow())
                        }
                    )
                ]
            )

        processed.append(url)

        save_state(run_id, {
            "status": "running",
            "processed_urls": processed,
            "last_updated": str(datetime.utcnow())
        })

    save_state(run_id, {
        "status": "completed",
        "processed_urls": processed,
        "completed_at": str(datetime.utcnow())
    })
