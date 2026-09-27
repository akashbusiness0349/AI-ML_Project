from __future__ import annotations

from .embeddings import SemanticEmbedder
from .vector_index import VectorIndex


class SemanticSearcher:
    def __init__(
        self,
        embedder: SemanticEmbedder,
        index: VectorIndex,
    ) -> None:
        self.embedder = embedder
        self.index = index

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        vector = self.embedder.transform([query])[0]
        return self.index.search(
            vector,
            top_k=top_k,
        )