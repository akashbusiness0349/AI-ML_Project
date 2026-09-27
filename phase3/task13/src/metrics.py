from __future__ import annotations

import math


def precision_at_k(
    ranked_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    top = ranked_ids[:k]

    if not top:
        return 0.0

    hits = sum(item in relevant_ids for item in top)

    return hits / len(top)


def recall_at_k(
    ranked_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    if not relevant_ids:
        return 0.0

    hits = sum(item in relevant_ids for item in ranked_ids[:k])

    return hits / len(relevant_ids)


def reciprocal_rank(
    ranked_ids: list[str],
    relevant_ids: set[str],
) -> float:
    for position, item in enumerate(ranked_ids, start=1):
        if item in relevant_ids:
            return 1.0 / position

    return 0.0


def ndcg_at_k(
    ranked_ids: list[str],
    relevance: dict[str, int],
    k: int,
) -> float:

    def dcg(items: list[str]) -> float:
        total = 0.0

        for index, item in enumerate(items, start=1):
            gain = 2 ** relevance.get(item, 0) - 1
            total += gain / math.log2(index + 1)

        return total

    actual = dcg(ranked_ids[:k])

    ideal_items = sorted(
        relevance,
        key=lambda item: (-relevance[item], item),
    )

    ideal = dcg(ideal_items[:k])

    if ideal == 0:
        return 0.0

    return actual / ideal


def mean_reciprocal_rank(
    rankings,
    relevance_sets=None,
) -> float:

    if relevance_sets is None:
        parsed_predictions = []
        parsed_relevance = []

        for ranking, relevant in rankings:
            parsed_predictions.append(ranking)
            parsed_relevance.append(set(relevant))

        rankings = parsed_predictions
        relevance_sets = parsed_relevance

    if not rankings:
        return 0.0

    values = [
        reciprocal_rank(pred, rel)
        for pred, rel in zip(rankings, relevance_sets)
    ]

    return sum(values) / len(values)


def evaluate_rankings(
    predictions,
    relevance_sets=None,
    relevance_scores=None,
    k: int = 5,
) -> dict:

    # Support the test-friendly format:
    #
    # [
    #   {
    #       "query_id": "...",
    #       "ranked_ids": [...],
    #       "relevant_ids": {...}
    #   }
    # ]
    #
    if (
        predictions
        and isinstance(predictions[0], dict)
        and "ranked_ids" in predictions[0]
    ):
        rows = predictions

        rankings = [
            row["ranked_ids"]
            for row in rows
        ]

        relevance_sets = [
            set(row["relevant_ids"])
            for row in rows
        ]

        relevance_scores = [
            {
                doc_id: 1
                for doc_id in row["relevant_ids"]
            }
            for row in rows
        ]

    else:
        rankings = predictions

        if relevance_sets is None:
            relevance_sets = [set() for _ in rankings]

        if relevance_scores is None:
            relevance_scores = [
                {doc_id: 1 for doc_id in rel}
                for rel in relevance_sets
            ]

    if not rankings:
        return {
            f"precision@{k}": 0.0,
            f"Precision@{k}": 0.0,
            f"recall@{k}": 0.0,
            f"Recall@{k}": 0.0,
            "MRR": 0.0,
            f"nDCG@{k}": 0.0,
        }

    precision = []
    recall = []
    mrr = []
    ndcg = []

    for ranked, relevant, scores in zip(
        rankings,
        relevance_sets,
        relevance_scores,
    ):
        precision.append(
            precision_at_k(ranked, relevant, k)
        )

        recall.append(
            recall_at_k(ranked, relevant, k)
        )

        mrr.append(
            reciprocal_rank(ranked, relevant)
        )

        ndcg.append(
            ndcg_at_k(ranked, scores, k)
        )

    precision_value = sum(precision) / len(precision)
    recall_value = sum(recall) / len(recall)
    mrr_value = sum(mrr) / len(mrr)
    ndcg_value = sum(ndcg) / len(ndcg)

    return {
        f"precision@{k}": precision_value,
        f"recall@{k}": recall_value,
        "MRR": mrr_value,
        f"nDCG@{k}": ndcg_value,

        # Backward-compatible keys.
        f"Precision@{k}": precision_value,
        f"Recall@{k}": recall_value,
    }
