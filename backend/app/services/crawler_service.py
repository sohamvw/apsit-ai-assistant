import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


def crawl_website(start_url, max_pages=50):
    visited = set()
    queue = deque([start_url])
    results = []

    base_domain = urlparse(start_url).netloc

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
        results.append(url)

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            absolute_url = urljoin(url, link["href"])
            parsed = urlparse(absolute_url)

            if parsed.netloc == base_domain:
                if absolute_url not in visited:
                    queue.append(absolute_url)

    return results
