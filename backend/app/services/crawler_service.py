from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

BASE_DOMAIN = "apsit.edu.in"
MAX_PAGES = 200        # safety limit
TIMEOUT = 10


def is_internal(url):
    parsed = urlparse(url)
    return BASE_DOMAIN in parsed.netloc


def normalize_url(url):
    # Remove fragments like #section
    url, _ = urldefrag(url)
    return url.rstrip("/")


def crawl(start_url):
    visited = set()
    to_visit = [normalize_url(start_url)]
    pages_crawled = 0

    while to_visit and pages_crawled < MAX_PAGES:
        url = to_visit.pop(0)  # BFS (better for wide crawl)

        if url in visited:
            continue

        visited.add(url)

        try:
            response = requests.get(url, timeout=TIMEOUT)

            content_type = response.headers.get("content-type", "")

            print("Crawling:", url)

            yield url, content_type, response.content

            pages_crawled += 1

            # Only parse HTML for new links
            if "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")

                for a in soup.find_all("a", href=True):
                    link = urljoin(url, a["href"])
                    link = normalize_url(link)

                    if is_internal(link) and link not in visited:
                        to_visit.append(link)

        except Exception as e:
            print("Crawler error:", e)
            continue
