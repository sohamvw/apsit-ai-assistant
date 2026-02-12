import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


def crawl_website(start_url, max_pages=500):
    visited = set()
    queue = deque([start_url])
    results = []

    base_domain = urlparse(start_url).netloc.replace("www.", "")

    while queue and len(visited) < max_pages:
        url = queue.popleft()

        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except:
            continue

        visited.add(url)

        content_type = response.headers.get("Content-Type", "")

        results.append(
            (url, content_type, response.content)
        )

        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(url, link["href"])
                parsed = urlparse(absolute_url)

                clean_domain = parsed.netloc.replace("www.", "")

                if clean_domain == base_domain:
                    clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path

                    if clean_url not in visited:
                        queue.append(clean_url)

    return results
