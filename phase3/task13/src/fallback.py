from __future__ import annotations

from .keyword_search import KeywordSearcher


class SearchFallback:
    def __init__(
        self,
        keyword_searcher: KeywordSearcher,
    ) -> None:
        self.keyword_searcher = keyword_searcher

    def search(
        self,
        query: str,
        top_k: int = 10,
        reason: str = "SEMANTIC_UNAVAILABLE",
    ) -> dict:
        results = self.keyword_searcher.search(
            query,
            top_k=top_k,
        )

        return {
            "status": "FALLBACK",
            "reason": reason,
            "retrieval_mode": "keyword_fallback",
            "results": results,
        }