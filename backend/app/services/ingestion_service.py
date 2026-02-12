from app.services.crawler_service import crawl_website
from app.services.file_extractors import (
    extract_html,
    extract_pdf,
    extract_docx,
    extract_xlsx,
    extract_pptx,
)
from app.services.vector_service import insert_document
import time


def run_ingestion():
    start_url = "https://www.apsit.edu.in/"

    print("Starting crawl...")

    pages = crawl_website(start_url, max_pages=1000)

    count = 0

    for url, content_type, content in pages:
        try:
            if "text/html" in content_type:
                text = extract_html(content)

            elif "application/pdf" in content_type:
                text = extract_pdf(content)

            elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
                text = extract_docx(content)

            elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type:
                text = extract_xlsx(content)

            elif "application/vnd.openxmlformats-officedocument.presentationml.presentation" in content_type:
                text = extract_pptx(content)

            else:
                continue

            if text and len(text.strip()) > 300:
                insert_document(text[:8000], url)
                count += 1
                print("Ingested: {url}")

            time.sleep(0.2)

        except Exception as e:
            print("Failed: {url} -> {e}")

    print("Ingestion completed. Total inserted: {count}")
