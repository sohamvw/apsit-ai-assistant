# scan_site.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.apsit.edu.in/"

visited = set()
files = {"pdf": [], "doc": [], "xls": [], "images": [], "html": []}

def crawl(url):
    if url in visited:
        return
    visited.add(url)

    try:
        r = requests.get(url, timeout=10)
    except:
        return

    if "text/html" in r.headers.get("Content-Type", ""):
        files["html"].append(url)
        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = urljoin(BASE, link["href"])

            if href.endswith(".pdf"):
                files["pdf"].append(href)
            elif href.endswith(".doc") or href.endswith(".docx"):
                files["doc"].append(href)
            elif href.endswith(".xls") or href.endswith(".xlsx"):
                files["xls"].append(href)
            elif any(href.endswith(ext) for ext in [".png",".jpg",".jpeg"]):
                files["images"].append(href)
            elif BASE in href:
                crawl(href)

crawl(BASE)

for k,v in files.items():
    print(k, len(v))
