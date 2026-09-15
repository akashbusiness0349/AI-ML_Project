from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable


def percentile(
    values: list[float],
    p: float
) -> float:

    if not values:
        return 0.0

    ordered = sorted(values)

    rank = (
        len(ordered) - 1
    ) * (p / 100.0)

    lower = int(rank)

    upper = min(
        lower + 1,
        len(ordered) - 1
    )

    fraction = rank - lower

    return (
        ordered[lower] * (1.0 - fraction)
        + ordered[upper] * fraction
    )


def profile_stages(
    stage_functions: dict[str, Callable[[], object]],
    iterations: int,
) -> dict:

    samples = defaultdict(list)

    for _ in range(iterations):

        for name, function in stage_functions.items():

            start = time.perf_counter_ns()

            function()

            elapsed_ms = (
                time.perf_counter_ns() - start
            ) / 1_000_000.0

            samples[name].append(elapsed_ms)

    summary = {}

    for name, values in samples.items():

        summary[name] = {
            "avg_ms": sum(values) / len(values),
            "p95_ms": percentile(values, 95),
            "p99_ms": percentile(values, 99),
            "max_ms": max(values),
        }

    bottleneck = max(
        summary,
        key=lambda name:
        summary[name]["p95_ms"]
    )

    return {
        "iterations": iterations,
        "stages": summary,
        "bottleneck_by_p95": bottleneck,
        "measurement_unit": "milliseconds",
        "clock": "time.perf_counter_ns",
    }