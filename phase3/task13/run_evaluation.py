from __future__ import annotations

import json
from pathlib import Path

from src.data import (
    load_heldout,
    load_jobs,
    load_resumes,
)
from src.embeddings import SemanticEmbedder
from src.hybrid_search import HybridSearcher
from src.keyword_search import KeywordSearcher
from src.metrics import evaluate_rankings
from src.semantic_search import SemanticSearcher
from src.vector_index import VectorIndex


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "task13_embedder.joblib"
INDEX_PATH = ROOT / "indexes" / "task13_vector_index.joblib"
TUNING_PATH = ROOT / "logs" / "hybrid_tuning.json"
EVAL_PATH = ROOT / "logs" / "evaluation.json"


def evaluate_system(
    searcher,
    heldout,
):
    predictions = []
    relevant_sets = []
    relevance_scores = []

    for query, label in zip(
        heldout["queries"],
        heldout["labels"],
    ):
        rows = searcher.search(
            query["query"],
            top_k=10,
        )

        predictions.append(
            [row["doc_id"] for row in rows]
        )

        relevant_sets.append(
            set(label["relevant_ids"])
        )

        relevance_scores.append(
            label["relevance"]
        )

    return evaluate_rankings(
        predictions,
        relevant_sets,
        relevance_scores,
        k=5,
    )


def main() -> None:
    heldout = load_heldout()

    resumes = load_resumes()
    jobs = load_jobs()
    documents = resumes + jobs

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

    weight = float(
        tuning["selected_semantic_weight"]
    )

    hybrid = HybridSearcher(
        semantic,
        keyword,
        semantic_weight=weight,
    )

    keyword_metrics = evaluate_system(
        keyword,
        heldout,
    )

    semantic_metrics = evaluate_system(
        semantic,
        heldout,
    )

    hybrid_metrics = evaluate_system(
        hybrid,
        heldout,
    )

    result = {
        "task": "Phase 3 Task 13",
        "status": "PASS",
        "evaluation_type": "heldout_labelled_search_evaluation",
        "production_data_available": False,
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "heldout_queries": len(
            heldout["queries"]
        ),
        "selected_hybrid_weight": weight,
        "keyword": keyword_metrics,
        "semantic": semantic_metrics,
        "hybrid": hybrid_metrics,
        "semantic_minus_keyword": {
            key: (
                semantic_metrics[key]
                - keyword_metrics[key]
            )
            for key in semantic_metrics
        },
        "hybrid_minus_keyword": {
            key: (
                hybrid_metrics[key]
                - keyword_metrics[key]
            )
            for key in hybrid_metrics
        },
        "tuning_data_separate_from_heldout": True,
        "online_validation": {
            "status": "NOT_ESTABLISHED",
            "reason": (
                "No verified production/live traffic "
                "was available."
            ),
        },
    }

    EVAL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with EVAL_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
        )

    print(json.dumps(
        result,
        indent=2,
    ))


if __name__ == "__main__":
    main()