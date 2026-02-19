import uuid
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from .collection_manager import get_qdrant_client, COLLECTION_NAME


def generate_chunk_id(url: str, chunk_index: int) -> str:
    """
    Generate deterministic UUID based on URL + chunk index.
    """
    base_string = f"{url}_{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base_string))


def delete_existing_chunks(url: str):
    client = get_qdrant_client()

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="url",
                    match=MatchValue(value=url),
                )
            ]
        ),
    )

    print(f"Deleted existing chunks for {url}")


def upsert_chunks(url, chunks, embeddings, metadata_list):
    client = get_qdrant_client()

    # Overwrite mode
    delete_existing_chunks(url)

    points = []

    for idx, (chunk, embedding, metadata) in enumerate(
        zip(chunks, embeddings, metadata_list)
    ):
        point = PointStruct(
            id=generate_chunk_id(url, idx),  # now valid UUID
            vector=embedding,
            payload={
                "text": chunk,
                **metadata,
            },
        )
        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(f"Upserted {len(points)} chunks for {url}")
