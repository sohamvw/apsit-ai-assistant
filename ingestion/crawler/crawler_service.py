import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

MAX_PAGES = 50   # control crawl size
TIMEOUT = 10


def crawl_site(start_url: str, domain: str):
    visited = set()
    queue = deque([start_url])
    documents = []

    while queue and len(visited) < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        try:
            print(f"🔍 Crawling: {url}")
            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract visible text
            text = soup.get_text(separator=" ", strip=True)

            documents.append({
                "url": url,
                "text": text
            })

            visited.add(url)

            # Find internal links
            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                parsed = urlparse(absolute_url)

                # Only same domain
                if domain in parsed.netloc:
                    clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path

                    if clean_url not in visited:
                        queue.append(clean_url)

        except Exception as e:
            print(f"❌ Failed: {url} | {e}")
            continue

    print(f"✅ Crawled {len(documents)} pages.")
    return documents
