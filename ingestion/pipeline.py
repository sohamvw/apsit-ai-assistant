from crawler.crawler_service import crawl_site
from processing.hash_compare import (
    generate_hash,
    has_content_changed,
    update_hash,
)
from processing.chunker import chunk_text
from embedding.text_embedder import TextEmbedder
from qdrant.upsert_service import upsert_chunks


def run_pipeline():
    start_url = "https://apsit.edu.in"
    domain = "apsit.edu.in"

    embedder = TextEmbedder()

    documents = crawl_site(start_url, domain)

    print(f"📄 Total documents found: {len(documents)}")

    for doc in documents:
        combined_text = f"{doc['title']} {doc['text']} {doc['image_alt_text']}"

        content_hash = generate_hash(combined_text)

        if not has_content_changed(doc["url"], content_hash):
            print(f"Skipping unchanged page: {doc['url']}")
            continue

        chunks = chunk_text(combined_text)

        if not chunks:
            continue

        embeddings = embedder.embed_documents(chunks)

        metadata_list = [
            {
                "url": doc["url"],
                "title": doc["title"],
                "source_type": "html",
            }
            for _ in chunks
        ]

        upsert_chunks(doc["url"], chunks, embeddings, metadata_list)

        update_hash(doc["url"], content_hash)


if __name__ == "__main__":
    run_pipeline()
