from __future__ import annotations

from collections import Counter
from typing import Mapping


def estimate_position_propensity(
    impressions: list[Mapping],
) -> dict[int, dict[str, float]]:
    counts = Counter(
        int(row["position"])
        for row in impressions
    )

    total = sum(counts.values())

    if total == 0:
        return {}

    result = {}

    for position in sorted(counts):
        propensity = counts[position] / total

        propensity = max(
            propensity,
            0.01,
        )

        result[position] = {
            "estimated_propensity": float(
                propensity
            ),
            "inverse_weight": float(
                1.0 / propensity
            ),
        }

    return result


def inverse_propensity_weight(
    position: int,
    propensity_table: Mapping,
) -> float:
    row = propensity_table.get(position)

    if row is None:
        return 1.0

    return float(
        row["inverse_weight"]
    )


def apply_position_bias_weights(
    impressions: list[Mapping],
) -> tuple[list[float], dict]:
    table = estimate_position_propensity(
        impressions
    )

    weights = [
        inverse_propensity_weight(
            int(row["position"]),
            table,
        )
        for row in impressions
    ]

    return weights, table