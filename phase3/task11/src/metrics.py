from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Mapping


def dcg(relevances: Iterable[float], k: int) -> float:
    score = 0.0

    for index, relevance in enumerate(
        list(relevances)[:k],
        start=1,
    ):
        score += (
            (2.0 ** float(relevance) - 1.0)
            / math.log2(index + 1.0)
        )

    return score


def ndcg(
    ranked_relevances: Iterable[float],
    ideal_relevances: Iterable[float],
    k: int,
) -> float:
    ranked = list(ranked_relevances)[:k]
    ideal = sorted(
        list(ideal_relevances),
        reverse=True,
    )[:k]

    ideal_dcg = dcg(
        ideal,
        k,
    )

    if ideal_dcg <= 0.0:
        return 0.0

    return dcg(
        ranked,
        k,
    ) / ideal_dcg


def average_precision(
    ranked_relevances: Iterable[float],
) -> float:
    values = list(ranked_relevances)

    relevant_total = sum(
        1 for x in values
        if x > 0
    )

    if relevant_total == 0:
        return 0.0

    hits = 0
    precision_sum = 0.0

    for index, relevance in enumerate(
        values,
        start=1,
    ):
        if relevance > 0:
            hits += 1
            precision_sum += hits / index

    return precision_sum / relevant_total


def mean_average_precision(
    rankings: Iterable[Iterable[float]],
) -> float:
    values = list(rankings)

    if not values:
        return 0.0

    return sum(
        average_precision(row)
        for row in values
    ) / len(values)


def precision_at_k(
    relevances: Iterable[float],
    k: int,
) -> float:
    values = list(relevances)[:k]

    if not values:
        return 0.0

    return sum(
        1 for x in values
        if x > 0
    ) / len(values)


def group_impressions(
    impressions: list[Mapping],
) -> dict[str, list[Mapping]]:
    groups = defaultdict(list)

    for row in impressions:
        groups[
            row["session_id"]
        ].append(row)

    return dict(groups)


def evaluate_rankings(
    rankings: list[list[float]],
    k_values: tuple[int, ...] = (5, 10),
) -> dict:
    result = {
        "MAP": mean_average_precision(rankings),
    }

    for k in k_values:
        result[f"nDCG@{k}"] = (
            sum(
                ndcg(
                    row,
                    row,
                    k,
                )
                for row in rankings
            )
            / len(rankings)
            if rankings
            else 0.0
        )

        result[f"Precision@{k}"] = (
            sum(
                precision_at_k(row, k)
                for row in rankings
            )
            / len(rankings)
            if rankings
            else 0.0
        )

    return result