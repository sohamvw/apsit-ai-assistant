import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


def crawl_site(start_url: str, max_pages: int = 30):
    visited = set()
    to_visit = [start_url]
    results = []

    domain = urlparse(start_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            print(f"🔎 Crawling: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            text = soup.get_text(separator=" ", strip=True)

            results.append({
                "url": url,
                "text": text
            })

            visited.add(url)

            # Extract links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                if parsed.netloc == domain:
                    if full_url not in visited:
                        to_visit.append(full_url)

            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Failed to crawl {url}: {e}")

    print(f"✅ Crawled {len(results)} pages")
    return results
