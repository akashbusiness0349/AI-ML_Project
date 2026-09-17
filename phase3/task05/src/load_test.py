"""
HTTP load generator.

Uses Python standard-library networking so the experiment does
not depend on an additional HTTP client package.
"""

import json
import time
import urllib.request
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from typing import Dict, List

from .metrics import summarize


def send_request(
    url: str,
    payload: Dict,
    timeout: float = 15.0,
) -> dict:

    started = time.perf_counter()

    try:

        body = json.dumps(
            payload
        ).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=body,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            raw = response.read()

            latency_ms = (
                time.perf_counter()
                - started
            ) * 1000.0

            parsed = json.loads(
                raw.decode("utf-8")
            )

            if response.status >= 400:
                return {
                    "success": False,
                    "latency_ms": latency_ms,
                    "response": parsed,
                    "error": (
                        f"HTTP_{response.status}"
                    ),
                }

            if (
                parsed.get("error_code")
                == "MODEL_UNAVAILABLE"
            ):
                return {
                    "success": False,
                    "latency_ms": latency_ms,
                    "response": parsed,
                    "error": "MODEL_UNAVAILABLE",
                }

            return {
                "success": True,
                "latency_ms": latency_ms,
                "response": parsed,
                "error": None,
            }

    except Exception as exc:

        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000.0

        return {
            "success": False,
            "latency_ms": latency_ms,
            "response": None,
            "error": type(exc).__name__,
        }


def run_load_level(
    url: str,
    requests: List[Dict],
    concurrency: int,
    requests_per_level: int,
) -> dict:

    payloads = [
        requests[
            index % len(requests)
        ]
        for index in range(
            requests_per_level
        )
    ]

    latencies = []
    errors = 0

    started = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = [
            executor.submit(
                send_request,
                url,
                payload,
            )
            for payload in payloads
        ]

        for future in as_completed(
            futures
        ):

            result = future.result()

            if result["success"]:
                latencies.append(
                    result["latency_ms"]
                )
            else:
                errors += 1

    duration = (
        time.perf_counter()
        - started
    )

    metrics = summarize(
        latencies_ms=latencies,
        errors=errors,
        duration_seconds=duration,
    )

    return {
        "concurrency": concurrency,
        "metrics": metrics,
    }


def run_sweep(
    url: str,
    requests: List[Dict],
    concurrency_levels: List[int],
    requests_per_level: int,
) -> List[Dict]:

    results = []

    for concurrency in concurrency_levels:

        print(
            f"\nTesting concurrency={concurrency}"
        )

        result = run_load_level(
            url=url,
            requests=requests,
            concurrency=concurrency,
            requests_per_level=requests_per_level,
        )

        results.append(result)

        metrics = result["metrics"]

        print(
            f"  p50  : {metrics['p50_ms']:.3f} ms"
        )

        print(
            f"  p95  : {metrics['p95_ms']:.3f} ms"
        )

        print(
            f"  p99  : {metrics['p99_ms']:.3f} ms"
        )

        print(
            f"  QPS  : {metrics['qps']:.3f}"
        )

        print(
            f"  Error: "
            f"{metrics['error_rate_percent']:.3f}%"
        )

    return results