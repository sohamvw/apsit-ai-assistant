import hashlib
import json
import os

PROGRESS_FILE = "ingestion_progress.json"


def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress_data: dict):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2)


def has_content_changed(url: str, new_hash: str) -> bool:
    progress_data = load_progress()

    if url not in progress_data:
        return True

    return progress_data[url] != new_hash


def update_hash(url: str, new_hash: str):
    progress_data = load_progress()
    progress_data[url] = new_hash
    save_progress(progress_data)
