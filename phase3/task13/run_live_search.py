from __future__ import annotations

import json
import sys
from pathlib import Path

from src.data import all_documents
from src.embeddings import SemanticEmbedder
from src.fallback import SearchFallback
from src.hybrid_search import HybridSearcher
from src.keyword_search import KeywordSearcher
from src.semantic_search import SemanticSearcher
from src.serving import SearchService
from src.vector_index import VectorIndex


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "task13_embedder.joblib"
INDEX_PATH = ROOT / "indexes" / "task13_vector_index.joblib"
TUNING_PATH = ROOT / "logs" / "hybrid_tuning.json"


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()

    if not query:
        query = "someone who can build data pipelines"

    documents = all_documents()

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

    fallback = SearchFallback(
        keyword
    )

    service = SearchService(
        hybrid=hybrid,
        fallback=fallback,
    )

    result = service.search(
        query,
        top_k=5,
        explain=True,
    )

    print(json.dumps(
        result,
        indent=2,
    ))


if __name__ == "__main__":
    main()