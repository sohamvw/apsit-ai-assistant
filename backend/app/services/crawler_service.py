from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

BASE_DOMAIN = "apsit.edu.in"

def is_internal(url):
    return BASE_DOMAIN in urlparse(url).netloc

def crawl(start_url):
    visited = set()
    to_visit = [start_url]

    while to_visit:
        url = to_visit.pop()

        if url in visited:
            continue

        visited.add(url)

        try:
            r = requests.get(url, timeout=10)
            content_type = r.headers.get("content-type", "")

            yield url, content_type, r.content

            if "text/html" in content_type:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    link = urljoin(url, a["href"])
                    if is_internal(link):
                        to_visit.append(link)

        except Exception:
            continue
