import uuid
import traceback
from datetime import datetime
from qdrant_client.models import PointStruct

from app.services.vector_service import (
    client,
    get_dense_embedding,
    create_collections,
)

from .crawler_service import crawl
from .file_extractors import *


DOC_COLLECTION = "apsit_docs"
STATE_COLLECTION = "apsit_ingestion_state"
VECTOR_SIZE = 3072


# ==========================================
# SAVE INGESTION STATE
# ==========================================

def save_state(run_id: str, payload: dict):
    try:
        client.upsert(
            collection_name=STATE_COLLECTION,
            points=[
                PointStruct(
                    id=run_id,
                    vector=[0.0] * VECTOR_SIZE,
                    payload=payload
                )
            ]
        )
    except Exception as e:
        print("❌ Failed to save ingestion state:", str(e))


# ==========================================
# MAIN INGESTION
# ==========================================

def run_ingestion():

    # 🔥 Ensure collections exist
    create_collections()

    run_id = str(uuid.uuid4())
    processed = []

    # Mark ingestion started
    save_state(run_id, {
        "status": "running",
        "processed_urls": [],
        "started_at": str(datetime.utcnow())
    })

    try:

        for url, content_type, content in crawl("https://www.apsit.edu.in/"):

            try:
                text = ""

                # --------------------------
                # Extract Text
                # --------------------------
                if "text/html" in content_type:
                   text = extract_html(content)

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

                # --------------------------
                # Chunking
                # --------------------------
                chunks = [
                    text[i:i + 800]
                    for i in range(0, len(text), 800)
                ]

                # --------------------------
                # Store Each Chunk
                # --------------------------
                for chunk in chunks:

                    try:
                        embedding = get_dense_embedding(chunk)

                        client.upsert(
                            collection_name=DOC_COLLECTION,
                            points=[
                                PointStruct(
                                    id=str(uuid.uuid4()),
                                    vector=embedding,
                                    payload={
                                        "url": url,
                                        "chunk": chunk,
                                        "timestamp": str(datetime.utcnow())
                                    }
                                )
                            ]
                        )

                    except Exception as embed_error:
                        print("❌ Embedding error:", str(embed_error))
                        continue

                processed.append(url)

                # Update progress
                save_state(run_id, {
                    "status": "running",
                    "processed_urls": processed,
                    "last_updated": str(datetime.utcnow())
                })

            except Exception as url_error:
                print("❌ URL processing failed:", url)
                print(traceback.format_exc())
                continue

        # --------------------------
        # Completed
        # --------------------------
        save_state(run_id, {
            "status": "completed",
            "processed_urls": processed,
            "completed_at": str(datetime.utcnow())
        })

    except Exception as fatal_error:

        print("🔥 FATAL INGESTION ERROR")
        print(traceback.format_exc())

        save_state(run_id, {
            "status": "failed",
            "error": str(fatal_error),
            "processed_urls": processed,
            "failed_at": str(datetime.utcnow())
        })
