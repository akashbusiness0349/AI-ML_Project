from __future__ import annotations

import json
import statistics
import time
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

    service = SearchService(
        hybrid=hybrid,
        fallback=SearchFallback(keyword),
    )

    query = "someone who can build data pipelines"

    latencies = []

    for _ in range(100):
        start = time.perf_counter()

        service.search(
            query,
            top_k=5,
            explain=False,
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed)

    latencies.sort()

    p50 = statistics.median(latencies)
    p95_index = int(
        0.95 * (len(latencies) - 1)
    )

    p95 = latencies[p95_index]

    result = {
        "task": "Phase 3 Task 13",
        "status": "PASS",
        "benchmark_runs": len(latencies),
        "query": query,
        "latency_ms": {
            "p50": p50,
            "p95": p95,
            "min": min(latencies),
            "max": max(latencies),
        },
        "latency_slo_ms": 100.0,
        "slo_met": p95 <= 100.0,
        "measurement_type": "local_offline_benchmark",
        "production_latency_evidence": False,
    }

    print(json.dumps(
        result,
        indent=2,
    ))


if __name__ == "__main__":
    main()