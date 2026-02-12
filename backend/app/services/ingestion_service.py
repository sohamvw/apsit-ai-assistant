import uuid
from datetime import datetime
from qdrant_client.models import PointStruct

from app.services.vector_service import client, get_dense_embedding
from .crawler_service import crawl
from .file_extractors import *

DOC_COLLECTION = "apsit_docs"
STATE_COLLECTION = "apsit_ingestion_state"


def save_state(run_id, payload):
    client.upsert(
        collection_name=STATE_COLLECTION,
        points=[
            PointStruct(
                id=run_id,
                vector=[0.0] * 3072,  # must match collection vector size
                payload=payload
            )
        ]
    )


def run_ingestion():
    run_id = str(uuid.uuid4())
    processed = []

    # Mark ingestion as started
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

        # CHUNKING
        chunks = [text[i:i + 800] for i in range(0, len(text), 800)]

        for i, chunk in enumerate(chunks):
            point_id = f"{uuid.uuid4()}"

            # 🔥 REAL EMBEDDING (3072 dimensions)
            embedding = get_dense_embedding(chunk)

            client.upsert(
                collection_name=DOC_COLLECTION,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "url": url,
                            "chunk": chunk,
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

    # Mark ingestion as completed
    save_state(run_id, {
        "status": "completed",
        "processed_urls": processed,
        "completed_at": str(datetime.utcnow())
    })
