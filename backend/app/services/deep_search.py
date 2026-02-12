from app.services.hybrid_search import hybrid_search


def deep_search(query: str):
    results = hybrid_search(query)
    return results
