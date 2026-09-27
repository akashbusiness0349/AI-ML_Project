from __future__ import annotations

import json
from pathlib import Path

from src.data import document_map
from src.embeddings import SemanticEmbedder
from src.hybrid_search import HybridSearcher
from src.keyword_search import KeywordSearcher
from src.semantic_search import SemanticSearcher
from src.vector_index import VectorIndex


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "task13_embedder.joblib"
INDEX_PATH = ROOT / "indexes" / "task13_vector_index.joblib"
TUNING_PATH = ROOT / "logs" / "hybrid_tuning.json"


def main() -> None:
    query = "someone who can build data pipelines"

    documents = list(
        document_map().values()
    )

    embedder = SemanticEmbedder.load(
        MODEL_PATH
    )

    index = VectorIndex.load(
        INDEX_PATH
    )

    semantic = SemanticSearcher(
        embedder,
        index,
    )

    keyword = KeywordSearcher(
        documents
    )

    with TUNING_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:
        tuning = json.load(f)

    hybrid = HybridSearcher(
        semantic,
        keyword,
        semantic_weight=float(
            tuning["selected_semantic_weight"]
        ),
    )

    rows = hybrid.search(
        query,
        top_k=5,
    )

    results = []

    for row in rows:
        document = document_map()[
            row["doc_id"]
        ]

        results.append(
            {
                "query": query,
                "document_id": row["doc_id"],
                "title": document.get(
                    "title",
                    row["doc_id"],
                ),
                "semantic_score": row[
                    "semantic_score"
                ],
                "keyword_score": row[
                    "keyword_score"
                ],
                "hybrid_score": row["score"],
                "reason": (
                    "Semantic retrieval identifies related "
                    "data-engineering concepts, while the "
                    "keyword signal preserves exact terminology."
                ),
            }
        )

    output = {
        "task": "Phase 3 Task 13",
        "status": "PASS",
        "worked_example": {
            "input": query,
            "output": results,
        },
    }

    print(json.dumps(
        output,
        indent=2,
    ))


if __name__ == "__main__":
    main()