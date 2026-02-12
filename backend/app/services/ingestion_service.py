import uuid
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from .crawler_service import crawl
from .file_extractors import *

client = QdrantClient(url="YOUR_QDRANT_URL", api_key="YOUR_KEY")

DOC_COLLECTION = "apsit_docs"
STATE_COLLECTION = "apsit_ingestion_state"

def save_state(run_id, payload):
    client.upsert(
        collection_name=STATE_COLLECTION,
        points=[
            PointStruct(
                id=run_id,
                vector=[0.0],
                payload=payload
            )
        ]
    )

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

        if not text.strip():
            continue

        # CHUNKING
        chunks = [text[i:i+800] for i in range(0, len(text), 800)]

        for i, chunk in enumerate(chunks):
            point_id = f"{url}_{i}"

            client.upsert(
                collection_name=DOC_COLLECTION,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=[0.1]*768,  # replace with real embedding
                        payload={
                            "url": url,
                            "chunk": chunk
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
