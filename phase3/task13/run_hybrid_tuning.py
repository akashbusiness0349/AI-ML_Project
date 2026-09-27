from __future__ import annotations

import json
from pathlib import Path

from src.data import (
    document_map,
    document_text,
    load_train,
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
LOG_PATH = ROOT / "logs" / "hybrid_tuning.json"


def evaluate_weight(
    weight: float,
    train: dict,
    documents: list[dict],
    document_lookup: dict,
    semantic: SemanticSearcher,
    keyword: KeywordSearcher,
) -> float:
    hybrid = HybridSearcher(
        semantic,
        keyword,
        semantic_weight=weight,
    )

    predictions = []
    relevant_sets = []
    relevance_scores = []

    for query, label in zip(
        train["queries"],
        train["labels"],
    ):
        rows = hybrid.search(
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

    metrics = evaluate_rankings(
        predictions,
        relevant_sets,
        relevance_scores,
        k=5,
    )

    return metrics["MRR"]


def main() -> None:
    train = load_train()
    documents = [
        *__import__(
            "src.data",
            fromlist=["load_resumes"],
        ).load_resumes(),
        *__import__(
            "src.data",
            fromlist=["load_jobs"],
        ).load_jobs(),
    ]

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

    best_weight = None
    best_score = -1.0
    candidates = []

    for weight in [
        0.0,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
    ]:
        score = evaluate_weight(
            weight,
            train,
            documents,
            document_map(),
            semantic,
            keyword,
        )

        candidates.append(
            {
                "semantic_weight": weight,
                "MRR": score,
            }
        )

        if score > best_score:
            best_score = score
            best_weight = weight

    result = {
        "task": "Phase 3 Task 13",
        "status": "PASS",
        "tuning_split": "train",
        "metric": "MRR",
        "candidate_weights": candidates,
        "selected_semantic_weight": best_weight,
        "selected_keyword_weight": 1.0 - best_weight,
        "selected_train_MRR": best_score,
        "heldout_data_used_for_tuning": False,
    }

    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_PATH.open(
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