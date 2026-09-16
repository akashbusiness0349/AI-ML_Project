from __future__ import annotations

import time
from typing import Any, Dict, List, Sequence

from .load_generator import run_concurrent_requests
from .metrics import build_summary


DEFAULT_LATENCY_SLO_MS = 100.0
DEFAULT_ERROR_SLO_PERCENT = 1.0


def run_single_level(
    url: str,
    records: Sequence[Dict[str, Any]],
    concurrency: int,
    total_requests: int,
    timeout_seconds: float,
    latency_slo_ms: float = DEFAULT_LATENCY_SLO_MS,
    error_slo_percent: float = DEFAULT_ERROR_SLO_PERCENT,
) -> Dict[str, Any]:

    started = time.perf_counter()

    measurements = run_concurrent_requests(
        url=url,
        records=records,
        concurrency=concurrency,
        total_requests=total_requests,
        timeout_seconds=timeout_seconds,
    )

    elapsed_seconds = time.perf_counter() - started

    latencies = [
        measurement.latency_ms
        for measurement in measurements
    ]

    successful = [
        measurement
        for measurement in measurements
        if measurement.success
    ]

    failed = [
        measurement
        for measurement in measurements
        if not measurement.success
    ]

    summary = build_summary(
        latencies_ms=latencies,
        total_requests=len(measurements),
        successful_requests=len(successful),
        failed_requests=len(failed),
        elapsed_seconds=elapsed_seconds,
        concurrency=concurrency,
        latency_slo_ms=latency_slo_ms,
        error_slo_percent=error_slo_percent,
    )

    sample_errors = [
        measurement.error
        for measurement in failed[:10]
        if measurement.error
    ]

    return {
        **summary,
        "sample_errors": sample_errors,
    }


def run_load_sweep(
    url: str,
    records: Sequence[Dict[str, Any]],
    concurrency_levels: Sequence[int],
    requests_per_level: int,
    timeout_seconds: float,
    latency_slo_ms: float = DEFAULT_LATENCY_SLO_MS,
    error_slo_percent: float = DEFAULT_ERROR_SLO_PERCENT,
) -> List[Dict[str, Any]]:

    results: List[Dict[str, Any]] = []

    for concurrency in concurrency_levels:
        result = run_single_level(
            url=url,
            records=records,
            concurrency=concurrency,
            total_requests=requests_per_level,
            timeout_seconds=timeout_seconds,
            latency_slo_ms=latency_slo_ms,
            error_slo_percent=error_slo_percent,
        )

        results.append(result)

    return results