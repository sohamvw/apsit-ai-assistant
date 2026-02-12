from app.services.hybrid_search import hybrid_search


def deep_search(query: str):
    first_pass = hybrid_search(query, limit=8)

    expanded_query = query + " " + " ".join(first_pass[:3])

    second_pass = hybrid_search(expanded_query, limit=8)

    combined = list(dict.fromkeys(first_pass + second_pass))

    return combined
