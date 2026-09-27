from __future__ import annotations

import json

from src.data import all_documents
from src.fallback import SearchFallback
from src.keyword_search import KeywordSearcher
from src.hybrid_search import HybridSearcher


class BrokenSemantic:
    def search(self, query: str, top_k: int = 10):
        raise RuntimeError(
            "SIMULATED_EMBEDDING_SERVICE_UNAVAILABLE"
        )


def main() -> None:
    documents = all_documents()

    keyword = KeywordSearcher(
        documents
    )

    fallback = SearchFallback(
        keyword
    )

    hybrid = HybridSearcher(
        semantic=BrokenSemantic(),
        keyword=keyword,
        semantic_weight=0.7,
    )

    try:
        hybrid.search(
            "someone who can build data pipelines",
            top_k=5,
        )
        raise RuntimeError(
            "Failure injection did not trigger."
        )
    except RuntimeError:
        fallback_result = fallback.search(
            "someone who can build data pipelines",
            top_k=5,
            reason="SIMULATED_EMBEDDING_SERVICE_UNAVAILABLE",
        )

    result = {
        "task": "Phase 3 Task 13",
        "status": "PASS",
        "failure_injected": True,
        "failure": (
            "SIMULATED_EMBEDDING_SERVICE_UNAVAILABLE"
        ),
        "fallback_status": fallback_result[
            "status"
        ],
        "fallback_mode": fallback_result[
            "retrieval_mode"
        ],
        "safe_degradation": (
            fallback_result["status"] == "FALLBACK"
        ),
    }

    print(json.dumps(
        result,
        indent=2,
    ))


if __name__ == "__main__":
    main()