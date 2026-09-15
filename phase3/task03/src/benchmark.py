from __future__ import annotations

import time
from typing import Callable

from .profiler import percentile


def benchmark(
    fn: Callable[[object], object],
    requests: list[object],
    runs: int,
) -> dict:

    if not requests:
        raise ValueError(
            "Benchmark workload is empty"
        )

    samples = []

    checksum = 0

    for i in range(runs):

        request = requests[
            i % len(requests)
        ]

        start = time.perf_counter_ns()

        result = fn(request)

        elapsed_ms = (
            time.perf_counter_ns() - start
        ) / 1_000_000.0

        samples.append(elapsed_ms)

        if result.get("status") == "OK":

            checksum += len(
                result.get(
                    "matched_skills",
                    []
                )
            )

        else:

            checksum += 1

    return {
        "runs": runs,
        "workload_size": len(requests),
        "avg_ms": sum(samples) / len(samples),
        "median_ms": percentile(samples, 50),
        "p95_ms": percentile(samples, 95),
        "p99_ms": percentile(samples, 99),
        "min_ms": min(samples),
        "max_ms": max(samples),
        "checksum": checksum,
        "measurement_unit": "milliseconds",
        "clock": "time.perf_counter_ns",
    }


def compare(
    baseline: dict,
    optimized: dict,
    slo_ms: float,
) -> dict:

    baseline_p95 = baseline["p95_ms"]

    optimized_p95 = optimized["p95_ms"]

    reduction = (
        (
            baseline_p95
            - optimized_p95
        )
        / baseline_p95
        * 100.0
        if baseline_p95
        else 0.0
    )

    return {
        "baseline_p95_ms": baseline_p95,
        "optimized_p95_ms": optimized_p95,
        "p95_reduction_percent": reduction,
        "baseline_meets_slo": (
            baseline_p95 <= slo_ms
        ),
        "optimized_meets_slo": (
            optimized_p95 <= slo_ms
        ),
        "latency_slo_ms": slo_ms,
        "optimization_is_faster": (
            optimized_p95 < baseline_p95
        ),
    }