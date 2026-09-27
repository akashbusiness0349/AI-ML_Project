from __future__ import annotations

from .keyword_search import KeywordSearcher
from .semantic_search import SemanticSearcher


def minmax_scores(rows: list[dict]) -> dict[str, float]:
    if not rows:
        return {}

    values = [float(row["score"]) for row in rows]
    low = min(values)
    high = max(values)

    if high - low < 1e-12:
        return {
            row["doc_id"]: 0.0
            for row in rows
        }

    return {
        row["doc_id"]: (
            float(row["score"]) - low
        ) / (high - low)
        for row in rows
    }


class HybridSearcher:
    def __init__(
        self,
        semantic: SemanticSearcher,
        keyword: KeywordSearcher,
        semantic_weight: float = 0.7,
    ) -> None:
        if not 0.0 <= semantic_weight <= 1.0:
            raise ValueError(
                "semantic_weight must be between 0 and 1."
            )

        self.semantic = semantic
        self.keyword = keyword
        self.semantic_weight = semantic_weight

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        semantic_rows = self.semantic.search(
            query,
            top_k=len(self.keyword.documents),
        )

        keyword_rows = self.keyword.search(
            query,
            top_k=len(self.keyword.documents),
        )

        semantic_scores = minmax_scores(
            semantic_rows
        )
        keyword_scores = minmax_scores(
            keyword_rows
        )

        ids = set(semantic_scores) | set(keyword_scores)

        results = []

        for doc_id in ids:
            semantic_score = semantic_scores.get(
                doc_id,
                0.0,
            )
            keyword_score = keyword_scores.get(
                doc_id,
                0.0,
            )

            combined = (
                self.semantic_weight * semantic_score
                + (1.0 - self.semantic_weight)
                * keyword_score
            )

            results.append(
                {
                    "doc_id": doc_id,
                    "score": float(combined),
                    "semantic_score": float(
                        semantic_score
                    ),
                    "keyword_score": float(
                        keyword_score
                    ),
                }
            )

        results.sort(
            key=lambda row: (
                -row["score"],
                row["doc_id"],
            )
        )

        for position, row in enumerate(
            results[:top_k],
            start=1,
        ):
            row["position"] = position

        return results[:top_k]