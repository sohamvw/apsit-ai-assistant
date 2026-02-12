from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

BASE_DOMAIN = "apsit.edu.in"
MAX_PAGES = 500
TIMEOUT = 10


def is_internal(url):
    parsed = urlparse(url)
    return parsed.netloc.endswith(BASE_DOMAIN)


def crawl(start_url):
    visited = set()
    queue = [start_url]

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)

        if url in visited:
            continue

        try:
            print("Crawling:", url)

            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code != 200:
                continue

            content_type = response.headers.get("content-type", "")

            visited.add(url)

            yield url, content_type, response.content

            if "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")

                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()

                    if not href:
                        continue

                    full_url = urljoin(url, href)
                    full_url = full_url.split("#")[0]

                    if (
                        is_internal(full_url)
                        and full_url not in visited
                        and full_url.startswith("http")
                    ):
                        queue.append(full_url)

        except Exception as e:
            print("Crawler error:", e)
            continue
