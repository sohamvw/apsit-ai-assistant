import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def get_sitemap_urls(base_url: str):
    sitemap_url = f"{base_url.rstrip('/')}/sitemap.xml"

    try:
        print(f"🌐 Fetching sitemap: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=10)

        if response.status_code != 200:
            print("⚠ Sitemap not found. Falling back to crawler.")
            return []

        root = ET.fromstring(response.content)

        urls = []
        for url in root.findall(".//{*}loc"):
            urls.append(url.text.strip())

        print(f"✅ Found {len(urls)} URLs in sitemap.")
        return urls

    except Exception as e:
        print(f"❌ Sitemap parsing failed: {e}")
        return []
