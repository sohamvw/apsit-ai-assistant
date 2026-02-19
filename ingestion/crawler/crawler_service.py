import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from .sitemap_parser import get_sitemap_urls

MAX_PAGES = 50
TIMEOUT = 10

# Browser-like headers to avoid 406 block
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_url(url):
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return f"{scheme}://{netloc}{path}"


def same_domain(url, domain):
    parsed = urlparse(url)
    return domain in parsed.netloc.lower()


def extract_page_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        print(f"Status code: {response.status_code}")

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary tags
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ""

        image_alt_texts = [
            img.get("alt", "").strip()
            for img in soup.find_all("img")
            if img.get("alt")
        ]

        image_alt_text = " ".join(image_alt_texts)
        text = soup.get_text(separator=" ", strip=True)

        return {
            "url": url,
            "title": title,
            "text": text,
            "image_alt_text": image_alt_text,
        }

    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None


def recursive_crawl(start_url: str, domain: str):
    visited = set()
    queue = deque([normalize_url(start_url)])
    documents = []

    while queue and len(visited) < MAX_PAGES:
        current = queue.popleft()

        if current in visited:
            continue

        print(f"🔍 Crawling: {current}")

        page_data = extract_page_data(current)

        if not page_data:
            visited.add(current)
            continue

        documents.append(page_data)
        visited.add(current)

        try:
            response = requests.get(current, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                absolute = urljoin(current, link["href"])
                normalized = normalize_url(absolute)

                if same_domain(normalized, domain):
                    if normalized not in visited:
                        queue.append(normalized)

        except Exception:
            continue

    print(f"✅ Recursively crawled {len(documents)} pages.")
    return documents


def crawl_site(start_url: str, domain: str):
    sitemap_urls = get_sitemap_urls(start_url)

    if sitemap_urls:
        documents = []

        for url in sitemap_urls[:MAX_PAGES]:
            normalized = normalize_url(url)
            print(f"🔍 Crawling (sitemap): {normalized}")

            page_data = extract_page_data(normalized)

            if page_data:
                documents.append(page_data)

        print(f"✅ Crawled {len(documents)} sitemap pages.")
        return documents

    print("⚠ Sitemap not found. Falling back to crawler.")
    return recursive_crawl(start_url, domain)
