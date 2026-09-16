from __future__ import annotations

import math
from typing import Dict, Iterable, List


def percentile(values: Iterable[float], percentile_value: float) -> float:
    """
    Linear interpolation percentile.

    Returns 0.0 for an empty input.
    """

    data = sorted(float(value) for value in values)

    if not data:
        return 0.0

    if percentile_value <= 0:
        return data[0]

    if percentile_value >= 100:
        return data[-1]

    position = (len(data) - 1) * (percentile_value / 100.0)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return data[lower]

    fraction = position - lower

    return data[lower] + (
        data[upper] - data[lower]
    ) * fraction


def summarize_latencies(latencies_ms: Iterable[float]) -> Dict[str, float]:
    values = list(latencies_ms)

    return {
        "p50_ms": round(percentile(values, 50), 6),
        "p95_ms": round(percentile(values, 95), 6),
        "p99_ms": round(percentile(values, 99), 6),
        "min_ms": round(min(values), 6) if values else 0.0,
        "max_ms": round(max(values), 6) if values else 0.0,
        "mean_ms": round(
            sum(values) / len(values),
            6,
        )
        if values
        else 0.0,
    }


def calculate_qps(
    successful_requests: int,
    elapsed_seconds: float,
) -> float:

    if elapsed_seconds <= 0:
        return 0.0

    return successful_requests / elapsed_seconds


def calculate_error_rate(
    total_requests: int,
    failed_requests: int,
) -> float:

    if total_requests <= 0:
        return 0.0

    return (failed_requests / total_requests) * 100.0


def build_summary(
    latencies_ms: List[float],
    total_requests: int,
    successful_requests: int,
    failed_requests: int,
    elapsed_seconds: float,
    concurrency: int,
    latency_slo_ms: float = 100.0,
    error_slo_percent: float = 1.0,
) -> Dict[str, float | int | bool]:

    latency = summarize_latencies(latencies_ms)

    qps = calculate_qps(
        successful_requests,
        elapsed_seconds,
    )

    error_rate = calculate_error_rate(
        total_requests,
        failed_requests,
    )

    slo_pass = (
        latency["p95_ms"] <= latency_slo_ms
        and error_rate <= error_slo_percent
    )

    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "qps": round(qps, 6),
        "error_rate_percent": round(error_rate, 6),
        **latency,
        "latency_slo_ms": latency_slo_ms,
        "error_rate_slo_percent": error_slo_percent,
        "slo_pass": slo_pass,
    }