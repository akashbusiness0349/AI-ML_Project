from __future__ import annotations

from collections import Counter
from math import log2


def precision_at_k(
    recommended: list[str],
    relevant: set[str],
    k: int,
) -> float:
    top = recommended[:k]

    if not top:
        return 0.0

    hits = sum(1 for item in top if item in relevant)

    return hits / len(top)


def coverage(
    recommendation_lists: list[list[str]],
    catalog_size: int,
) -> float:
    if catalog_size <= 0:
        return 0.0

    unique_items = {
        item
        for rows in recommendation_lists
        for item in rows
    }

    return len(unique_items) / catalog_size


def diversity(
    recommendation_lists: list[list[str]],
) -> float:
    if not recommendation_lists:
        return 0.0

    pair_scores = []

    for rows in recommendation_lists:
        if len(rows) < 2:
            continue

        unique_count = len(set(rows))
        possible_pairs = len(rows) * (len(rows) - 1) / 2

        if possible_pairs:
            duplicate_pairs = (
                len(rows) * (len(rows) - 1)
                - unique_count * (unique_count - 1)
            ) / 2

            pair_scores.append(
                1.0 - duplicate_pairs / possible_pairs
            )

    if not pair_scores:
        return 1.0

    return sum(pair_scores) / len(pair_scores)


def ndcg_at_k(
    recommended: list[str],
    relevance: dict[str, float],
    k: int,
) -> float:
    def dcg(items):
        total = 0.0

        for index, item in enumerate(items, start=1):
            rel = float(relevance.get(item, 0.0))
            total += (2**rel - 1) / log2(index + 1)

        return total

    actual = dcg(recommended[:k])

    ideal = dcg(
        sorted(
            relevance,
            key=lambda item: -relevance[item],
        )[:k]
    )

    if ideal == 0:
        return 0.0

    return actual / ideal


def evaluate_recommendations(
    predictions: list[list[str]],
    relevance_sets: list[set[str]],
    catalog_size: int,
    k: int = 5,
) -> dict:
    precisions = [
        precision_at_k(
            predicted,
            relevant,
            k,
        )
        for predicted, relevant in zip(
            predictions,
            relevance_sets,
        )
    ]

    return {
        "Precision@5": (
            sum(precisions) / len(precisions)
            if precisions
            else 0.0
        ),
        "Coverage": coverage(
            predictions,
            catalog_size,
        ),
        "Diversity": diversity(
            predictions,
        ),
    }