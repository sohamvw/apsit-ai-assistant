from sentence_transformers import SentenceTransformer
from typing import List
import torch

MODEL_NAME = "intfloat/multilingual-e5-base"

class TextEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading embedding model on {self.device}...")
        self.model = SentenceTransformer(MODEL_NAME, device=self.device)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed document passages.
        """
        formatted_texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            formatted_texts,
            batch_size=16,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Embed search query.
        """
        formatted_query = f"query: {query}"
        embedding = self.model.encode(
            formatted_query,
            normalize_embeddings=True,
        )
        return embedding.tolist()
