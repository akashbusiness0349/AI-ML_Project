"""
Runtime performance metrics.
"""

import math
import statistics
from typing import List


def percentile(
    values: List[float],
    percentile_value: float,
) -> float:

    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (
        percentile_value / 100.0
    ) * (len(ordered) - 1)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower]
        + (
            ordered[upper]
            - ordered[lower]
        )
        * fraction
    )


def summarize(
    latencies_ms: List[float],
    errors: int,
    duration_seconds: float,
) -> dict:

    successful = len(latencies_ms)
    total = successful + errors

    if total <= 0:
        total = 1

    error_rate = (
        errors / total
    ) * 100.0

    availability = (
        successful / total
    ) * 100.0

    qps = (
        successful / duration_seconds
        if duration_seconds > 0
        else 0.0
    )

    return {
        "requests": total,
        "successful_requests": successful,
        "errors": errors,
        "error_rate_percent": round(
            error_rate,
            6,
        ),
        "availability_percent": round(
            availability,
            6,
        ),
        "p50_ms": round(
            percentile(
                latencies_ms,
                50,
            ),
            6,
        ),
        "p95_ms": round(
            percentile(
                latencies_ms,
                95,
            ),
            6,
        ),
        "p99_ms": round(
            percentile(
                latencies_ms,
                99,
            ),
            6,
        ),
        "mean_ms": round(
            statistics.mean(
                latencies_ms
            )
            if latencies_ms
            else 0.0,
            6,
        ),
        "qps": round(
            qps,
            6,
        ),
        "duration_seconds": round(
            duration_seconds,
            6,
        ),
    }