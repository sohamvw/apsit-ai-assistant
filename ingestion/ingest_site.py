import os
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from extract_knowledge import ingest_documents

PRIMARY_DOMAIN = "apsit.edu.in"
BASE_URL = "https://apsit.edu.in"
SITEMAP_URL = "https://www.apsit.edu.in/sitemap.xml"

SKIP_DOMAINS = {"elearn.apsit.edu.in"}

DATA_DIR = "auto_data"
HTML_DIR = os.path.join(DATA_DIR, "html")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")

os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

visited = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

# -------------------- helpers --------------------

def sanitize_filename(text: str) -> str:
    return re.sub(r"[<>:\"/\\\\|?*#]", "_", text)[:180]

def fetch(url):
    return requests.get(url, headers=HEADERS, timeout=20)

def is_allowed(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    if domain in SKIP_DOMAINS:
        return False
    if domain and PRIMARY_DOMAIN not in domain:
        return False
    return True

# -------------------- PDF --------------------

def download_pdf(url):
    name = sanitize_filename(url.split("/")[-1])
    path = os.path.join(PDF_DIR, name)

    if os.path.exists(path):
        return

    try:
        r = fetch(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"[PDF] {name}")
    except Exception:
        print(f"[PDF SKIPPED] {url}")

# -------------------- HTML --------------------

def save_html_text(url, html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    if not text:
        return
    filename = sanitize_filename(url) + ".txt"
    with open(os.path.join(HTML_DIR, filename), "w", encoding="utf-8") as f:
        f.write(text)

# -------------------- CRAWLER (fallback) --------------------

def crawl(url):
    url, _ = urldefrag(url)

    if url in visited:
        return
    visited.add(url)

    if not is_allowed(url):
        return

    print(f"[CRAWLING] {url}")

    try:
        res = fetch(url)
    except Exception:
        return

    if "text/html" not in res.headers.get("Content-Type", ""):
        return

    save_html_text(url, res.text)

    soup = BeautifulSoup(res.text, "html.parser")
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])
        if link.lower().endswith(".pdf"):
            download_pdf(link)
        else:
            crawl(link)

# -------------------- SITEMAP (primary) --------------------

def ingest_sitemap():
    print("[SITEMAP] Fetching sitemap...")
    try:
        r = fetch(SITEMAP_URL)
        r.raise_for_status()
    except Exception:
        print("[SITEMAP] Failed to fetch sitemap")
        return []

    urls = []
    root = ET.fromstring(r.text)
    for loc in root.iter():
        if loc.tag.endswith("loc"):
            url = loc.text.strip()
            if is_allowed(url):
                urls.append(url)

    print(f"[SITEMAP] Found {len(urls)} URLs")
    return urls

# -------------------- MAIN --------------------

def has_any_data():
    for _, _, files in os.walk(DATA_DIR):
        if files:
            return True
    return False

if __name__ == "__main__":
    sitemap_urls = ingest_sitemap()

    if sitemap_urls:
        for url in sitemap_urls:
            if url.lower().endswith(".pdf"):
                download_pdf(url)
            else:
                crawl(url)
    else:
        # fallback crawl if sitemap unavailable
        print("[FALLBACK] Sitemap unavailable, crawling seeds")
        seeds = [
            BASE_URL + "/about-us",
            BASE_URL + "/first-year-admissions-2018-19",
            BASE_URL + "/departments",
            BASE_URL + "/exam-rules-and-regulations",
            BASE_URL + "/career"
        ]
        for seed in seeds:
            crawl(seed)

    if has_any_data():
        ingest_documents(DATA_DIR)
    else:
        print("[ERROR] No data collected")
