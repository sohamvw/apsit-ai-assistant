from app.services.crawler_service import crawl_website
from app.services.file_extractors import extract_html
from app.services.vector_service import insert_document
from app.core.config import get_settings
import time

settings = get_settings()


def run_ingestion():
    start_url = "https://www.apsit.edu.in/"

    print("Starting crawl...")

    urls = crawl_website(start_url, max_pages=100)

    print(f"Found {len(urls)} pages")

    for url in urls:
        try:
            text = extract_html(url)

            if len(text) > 300:
                insert_document(text[:5000], url)
                print(f"Ingested: {url}")

            time.sleep(0.5)

        except Exception as e:
            print(f"Failed: {url} -> {e}")

    print("Ingestion completed")
