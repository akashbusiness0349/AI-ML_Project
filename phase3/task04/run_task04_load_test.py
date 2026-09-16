"""
Phase 3 - Task 04
Horizontal Scale & Load Readiness

Standalone reproducible HTTP concurrency load test.

This runner intentionally does not depend on the signatures of the
other Task 04 helper modules. It performs the concurrent HTTP test,
calculates latency/throughput/error metrics, identifies the first
SLO breach, calculates conservative headroom, builds a scaling plan,
and writes reproducible evidence artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ============================================================================
# PATHS
# ============================================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

DATA_FILE = DATA_DIR / "inference_requests.json"


# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_URL = os.getenv(
    "TASK04_SERVICE_URL",
    "http://127.0.0.1:8000/infer",
)

HEALTH_URL = os.getenv(
    "TASK04_HEALTH_URL",
    "http://127.0.0.1:8000/health",
)

P95_SLO_MS = float(
    os.getenv(
        "TASK04_P95_SLO_MS",
        "100",
    )
)

ERROR_RATE_SLO_PERCENT = float(
    os.getenv(
        "TASK04_ERROR_RATE_SLO_PERCENT",
        "1",
    )
)

REQUESTS_PER_LEVEL = int(
    os.getenv(
        "TASK04_REQUESTS_PER_LEVEL",
        "100",
    )
)

CONCURRENCY_LEVELS = [
    int(value.strip())
    for value in os.getenv(
        "TASK04_CONCURRENCY_LEVELS",
        "1,2,4,8,16,32,64,128",
    ).split(",")
    if value.strip()
]

TIMEOUT_SECONDS = float(
    os.getenv(
        "TASK04_TIMEOUT_SECONDS",
        "10",
    )
)

WARMUP_REQUESTS = int(
    os.getenv(
        "TASK04_WARMUP_REQUESTS",
        "10",
    )
)

HEADROOM_PERCENT = float(
    os.getenv(
        "TASK04_HEADROOM_PERCENT",
        "30",
    )
)


# ============================================================================
# OUTPUT FILES
# ============================================================================

LOAD_TEST_RESULTS_FILE = LOG_DIR / "load_test_results.json"
LATENCY_CURVE_FILE = LOG_DIR / "latency_curve.json"
THROUGHPUT_FILE = LOG_DIR / "throughput_results.json"
BREAKING_POINT_FILE = LOG_DIR / "breaking_point.json"
HEADROOM_FILE = LOG_DIR / "headroom_analysis.json"
SCALING_PLAN_FILE = LOG_DIR / "scaling_plan.json"
SUMMARY_FILE = LOG_DIR / "task04_summary.json"
EXPERIMENT_LOG_FILE = LOG_DIR / "experiment_log.csv"


# ============================================================================
# CONSOLE HELPERS
# ============================================================================

def print_section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================================
# JSON HELPERS
# ============================================================================

def save_json(path: Path, payload) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            payload,
            handle,
            indent=2,
        )


def load_json(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


# ============================================================================
# DATASET
# ============================================================================

def load_test_records() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    payload = load_json(DATA_FILE)

    if isinstance(payload, list):
        records = payload

    elif isinstance(payload, dict):

        if "records" in payload:
            records = payload["records"]

        elif "requests" in payload:
            records = payload["requests"]

        else:
            raise ValueError(
                "Dataset object must contain "
                "'records' or 'requests'."
            )

    else:
        raise ValueError(
            "Dataset must be a JSON list or object."
        )

    if not isinstance(records, list):
        raise ValueError(
            "Inference request records must be a list."
        )

    if not records:
        raise ValueError(
            "Inference request dataset is empty."
        )

    return records


# ============================================================================
# HTTP CLIENT
# ============================================================================

def post_json(
    url: str,
    payload: dict,
    timeout: float,
) -> dict:

    body = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    with urlopen(
        request,
        timeout=timeout,
    ) as response:

        response_body = response.read().decode(
            "utf-8"
        )

        return {
            "http_status": response.status,
            "body": json.loads(response_body),
        }


def check_health() -> dict:

    request = Request(
        HEALTH_URL,
        headers={
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(
        request,
        timeout=TIMEOUT_SECONDS,
    ) as response:

        body = response.read().decode(
            "utf-8"
        )

        return json.loads(body)


# ============================================================================
# REQUEST MEASUREMENT
# ============================================================================

def perform_request(
    request_id: int,
    payload: dict,
) -> dict:

    start = time.perf_counter()

    try:

        result = post_json(
            SERVICE_URL,
            payload,
            TIMEOUT_SECONDS,
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        body = result.get(
            "body",
            {},
        )

        http_status = result.get(
            "http_status"
        )

        application_status = body.get(
            "status"
        )

        success = (
            http_status == 200
            and application_status == "success"
        )

        return {
            "request_index": request_id,
            "success": success,
            "latency_ms": elapsed_ms,
            "http_status": http_status,
            "application_status": application_status,
            "error": None if success else (
                f"HTTP={http_status}, "
                f"status={application_status}"
            ),
            "response": body,
        }

    except HTTPError as exc:

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return {
            "request_index": request_id,
            "success": False,
            "latency_ms": elapsed_ms,
            "http_status": exc.code,
            "application_status": None,
            "error": f"HTTPError {exc.code}",
            "response": None,
        }

    except URLError as exc:

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return {
            "request_index": request_id,
            "success": False,
            "latency_ms": elapsed_ms,
            "http_status": None,
            "application_status": None,
            "error": f"URLError: {exc.reason}",
            "response": None,
        }

    except TimeoutError:

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return {
            "request_index": request_id,
            "success": False,
            "latency_ms": elapsed_ms,
            "http_status": None,
            "application_status": None,
            "error": "TimeoutError",
            "response": None,
        }

    except Exception as exc:

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return {
            "request_index": request_id,
            "success": False,
            "latency_ms": elapsed_ms,
            "http_status": None,
            "application_status": None,
            "error": f"{type(exc).__name__}: {exc}",
            "response": None,
        }


# ============================================================================
# PERCENTILES
# ============================================================================

def percentile(
    values: list[float],
    percent: float,
) -> float:

    if not values:
        return float("nan")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (
        (len(ordered) - 1)
        * percent
        / 100.0
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    weight = position - lower

    return (
        ordered[lower]
        + (
            ordered[upper]
            - ordered[lower]
        )
        * weight
    )


# ============================================================================
# SINGLE LOAD LEVEL
# ============================================================================

def run_load_level(
    concurrency: int,
    requests_per_level: int,
    records: list[dict],
) -> dict:

    print(
        f"Testing concurrency={concurrency} "
        f"with {requests_per_level} requests..."
    )

    measurements = []

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = []

        for index in range(
            requests_per_level
        ):

            payload = dict(
                records[
                    index % len(records)
                ]
            )

            future = executor.submit(
                perform_request,
                index,
                payload,
            )

            futures.append(future)

        for future in as_completed(
            futures
        ):

            measurements.append(
                future.result()
            )

    wall_time_seconds = (
        time.perf_counter() - start
    )

    latencies = [
        float(item["latency_ms"])
        for item in measurements
        if item.get("latency_ms") is not None
    ]

    successful = [
        item
        for item in measurements
        if item.get("success") is True
    ]

    failed = [
        item
        for item in measurements
        if item.get("success") is not True
    ]

    total = len(measurements)

    if total > 0:
        error_rate = (
            len(failed)
            / total
            * 100.0
        )
    else:
        error_rate = 100.0

    if wall_time_seconds > 0:
        qps = (
            total
            / wall_time_seconds
        )
    else:
        qps = 0.0

    result = {
        "timestamp_utc": now_utc(),
        "concurrency": concurrency,
        "requests_per_level": requests_per_level,
        "requests_completed": len(successful),
        "requests_failed": len(failed),
        "total_requests": total,
        "wall_time_seconds": round(
            wall_time_seconds,
            6,
        ),
        "p50_ms": round(
            percentile(latencies, 50),
            6,
        ) if latencies else None,
        "p95_ms": round(
            percentile(latencies, 95),
            6,
        ) if latencies else None,
        "p99_ms": round(
            percentile(latencies, 99),
            6,
        ) if latencies else None,
        "min_ms": round(
            min(latencies),
            6,
        ) if latencies else None,
        "max_ms": round(
            max(latencies),
            6,
        ) if latencies else None,
        "mean_ms": round(
            statistics.mean(latencies),
            6,
        ) if latencies else None,
        "qps": round(
            qps,
            6,
        ),
        "error_rate_percent": round(
            error_rate,
            6,
        ),
        "p95_slo_ms": P95_SLO_MS,
        "error_rate_slo_percent": (
            ERROR_RATE_SLO_PERCENT
        ),
        "p95_slo_pass": (
            bool(
                latencies
                and percentile(
                    latencies,
                    95,
                ) <= P95_SLO_MS
            )
        ),
        "error_rate_slo_pass": (
            error_rate
            <= ERROR_RATE_SLO_PERCENT
        ),
        "overall_slo_pass": (
            bool(
                latencies
                and percentile(
                    latencies,
                    95,
                ) <= P95_SLO_MS
                and error_rate
                <= ERROR_RATE_SLO_PERCENT
            )
        ),
        "sample_errors": [
            item.get("error")
            for item in failed[:10]
        ],
    }

    print(
        f"  p50={format_metric(result['p50_ms'])} ms | "
        f"p95={format_metric(result['p95_ms'])} ms | "
        f"p99={format_metric(result['p99_ms'])} ms | "
        f"QPS={format_metric(result['qps'])} | "
        f"errors={format_metric(result['error_rate_percent'])}% | "
        f"SLO={'PASS' if result['overall_slo_pass'] else 'BREACH'}"
    )

    return result


# ============================================================================
# WARMUP
# ============================================================================

def warmup(
    records: list[dict],
) -> None:

    if WARMUP_REQUESTS <= 0:
        return

    print(
        f"Running {WARMUP_REQUESTS} warm-up requests..."
    )

    for index in range(
        WARMUP_REQUESTS
    ):

        payload = dict(
            records[
                index % len(records)
            ]
        )

        try:
            result = post_json(
                SERVICE_URL,
                payload,
                TIMEOUT_SECONDS,
            )

            if result.get(
                "http_status"
            ) != 200:
                raise RuntimeError(
                    f"Warm-up HTTP status: "
                    f"{result.get('http_status')}"
                )

        except Exception as exc:
            raise RuntimeError(
                f"Warm-up failed at request "
                f"{index + 1}: {exc}"
            ) from exc

    print("Warm-up complete.")


# ============================================================================
# BREAKING POINT
# ============================================================================

def identify_breaking_point(
    results: list[dict],
) -> dict:

    ordered = sorted(
        results,
        key=lambda item: int(
            item["concurrency"]
        ),
    )

    for item in ordered:

        p95 = item.get(
            "p95_ms"
        )

        error_rate = item.get(
            "error_rate_percent"
        )

        p95_breach = (
            p95 is None
            or p95 > P95_SLO_MS
        )

        error_breach = (
            error_rate is None
            or error_rate
            > ERROR_RATE_SLO_PERCENT
        )

        if p95_breach or error_breach:

            reasons = []

            if p95_breach:
                reasons.append(
                    "p95_latency"
                )

            if error_breach:
                reasons.append(
                    "error_rate"
                )

            return {
                "status": "BREACH_FOUND",
                "breaking_point_concurrency": int(
                    item["concurrency"]
                ),
                "reason": reasons,
                "observed_p95_ms": p95,
                "observed_error_rate_percent": (
                    error_rate
                ),
                "p95_slo_ms": P95_SLO_MS,
                "error_rate_slo_percent": (
                    ERROR_RATE_SLO_PERCENT
                ),
            }

    highest = ordered[-1]

    return {
        "status": "NO_BREACH_IN_TESTED_RANGE",
        "breaking_point_concurrency": None,
        "highest_tested_concurrency": int(
            highest["concurrency"]
        ),
        "highest_tested_p95_ms": highest.get(
            "p95_ms"
        ),
        "highest_tested_error_rate_percent": (
            highest.get(
                "error_rate_percent"
            )
        ),
        "p95_slo_ms": P95_SLO_MS,
        "error_rate_slo_percent": (
            ERROR_RATE_SLO_PERCENT
        ),
        "interpretation": (
            "No SLO breach was observed within "
            "the tested concurrency range. "
            "This is not a production capacity claim; "
            "higher concurrency should be tested "
            "to establish a measured breaking point."
        ),
    }


# ============================================================================
# HEADROOM
# ============================================================================

def calculate_headroom(
    results: list[dict],
    breaking_point: dict,
) -> dict:

    safe_results = [
        item
        for item in results
        if item.get(
            "overall_slo_pass"
        ) is True
    ]

    if not safe_results:

        return {
            "status": "NO_SAFE_LEVEL",
            "headroom_percent_target": (
                HEADROOM_PERCENT
            ),
            "recommended_operating_concurrency": 0,
            "highest_safe_tested_concurrency": 0,
            "formula": (
                "safe concurrency × "
                "(1 - headroom target)"
            ),
        }

    highest_safe = max(
        safe_results,
        key=lambda item: int(
            item["concurrency"]
        ),
    )

    highest_safe_concurrency = int(
        highest_safe["concurrency"]
    )

    recommended_operating = max(
        1,
        math.floor(
            highest_safe_concurrency
            * (
                1
                - HEADROOM_PERCENT
                / 100.0
            )
        ),
    )

    breaking_value = breaking_point.get(
        "breaking_point_concurrency"
    )

    if breaking_value is not None:

        capacity_reference = (
            breaking_value
        )

        reference_type = (
            "measured_breaking_point"
        )

    else:

        capacity_reference = (
            highest_safe_concurrency
        )

        reference_type = (
            "highest_safe_tested_level"
        )

    return {
        "status": "CALCULATED",
        "headroom_percent_target": (
            HEADROOM_PERCENT
        ),
        "highest_safe_tested_concurrency": (
            highest_safe_concurrency
        ),
        "recommended_operating_concurrency": (
            recommended_operating
        ),
        "capacity_reference_concurrency": (
            capacity_reference
        ),
        "capacity_reference_type": (
            reference_type
        ),
        "formula": (
            "recommended operating concurrency = "
            "highest safe tested concurrency × "
            "(1 - headroom target)"
        ),
        "evidence_boundary": (
            "Headroom is derived from the tested "
            "local service capacity and is not a "
            "production traffic guarantee."
        ),
    }


# ============================================================================
# SCALING PLAN
# ============================================================================

def build_scaling_plan(
    results: list[dict],
    breaking_point: dict,
    headroom: dict,
) -> dict:

    return {
        "strategy": "horizontal_scaling",
        "objective": (
            "Maintain the inference SLO while "
            "increasing concurrent request capacity."
        ),
        "autoscaling_signals": [
            {
                "signal": "request_concurrency",
                "action": (
                    "Scale out when sustained "
                    "concurrency approaches the "
                    "configured operating threshold."
                ),
            },
            {
                "signal": "p95_latency_ms",
                "action": (
                    "Scale out before p95 approaches "
                    f"the {P95_SLO_MS} ms SLO."
                ),
            },
            {
                "signal": "error_rate_percent",
                "action": (
                    "Scale out or fail safe when error "
                    f"rate approaches {ERROR_RATE_SLO_PERCENT}%."
                ),
            },
            {
                "signal": "cpu_utilization",
                "action": (
                    "Use sustained CPU utilization as "
                    "a supporting infrastructure signal."
                ),
            },
        ],
        "replica_policy": {
            "min_replicas": 1,
            "recommended_initial_max_replicas": 4,
            "scale_out_step": 1,
            "scale_in_step": 1,
            "scale_out_cooldown_seconds": 60,
            "scale_in_cooldown_seconds": 300,
        },
        "operating_policy": {
            "recommended_operating_concurrency": (
                headroom.get(
                    "recommended_operating_concurrency"
                )
            ),
            "headroom_percent": HEADROOM_PERCENT,
        },
        "batching": {
            "enabled_by_default": False,
            "recommendation": (
                "Enable micro-batching only if "
                "queueing delay remains inside the "
                "p95 latency SLO."
            ),
        },
        "precompute": {
            "recommended": True,
            "examples": [
                "cache normalized skill vocabulary",
                "precompute reusable feature mappings",
                "reuse immutable model artifacts",
            ],
        },
        "model_cache": {
            "recommended": True,
            "requirement": (
                "Load the model once per worker/replica "
                "instead of loading it for every request."
            ),
        },
        "rollback": {
            "trigger": [
                f"p95 latency > {P95_SLO_MS} ms",
                (
                    "error rate > "
                    f"{ERROR_RATE_SLO_PERCENT}%"
                ),
                "model readiness failure",
            ],
            "action": [
                "stop scale-in",
                "preserve minimum healthy replicas",
                "route traffic only to ready replicas",
                "return MODEL_UNAVAILABLE safe fallback "
                "when inference is unavailable",
            ],
        },
        "devops_handoff": [
            "Expose p50/p95/p99 latency metrics.",
            "Expose request/error counters.",
            "Expose model readiness health check.",
            "Configure autoscaling using concurrency "
            "and latency signals.",
            "Load-test every material serving change.",
            "Keep the 30% headroom policy unless production "
            "measurements justify another value.",
        ],
        "measured_breaking_point": breaking_point,
    }


# ============================================================================
# CSV EVIDENCE
# ============================================================================

def write_experiment_log(
    results: list[dict],
) -> None:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "timestamp_utc",
        "service_url",
        "concurrency",
        "requests_per_level",
        "requests_completed",
        "requests_failed",
        "total_requests",
        "wall_time_seconds",
        "p50_ms",
        "p95_ms",
        "p99_ms",
        "min_ms",
        "max_ms",
        "mean_ms",
        "qps",
        "error_rate_percent",
        "p95_slo_ms",
        "error_rate_slo_percent",
        "p95_slo_pass",
        "error_rate_slo_pass",
        "overall_slo_pass",
    ]

    with EXPERIMENT_LOG_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for item in results:

            writer.writerow(
                {
                    key: item.get(key)
                    for key in fieldnames
                }
            )


# ============================================================================
# FORMATTING
# ============================================================================

def format_metric(value) -> str:

    if value is None:
        return "n/a"

    try:
        return f"{float(value):.3f}"
    except (
        TypeError,
        ValueError,
    ):
        return "n/a"


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    print_section(
        "PHASE 3 - TASK 04\n"
        "HORIZONTAL SCALE & LOAD READINESS"
    )

    print(
        f"Service URL          : {SERVICE_URL}"
    )

    records = load_test_records()

    print(
        f"Request records      : {len(records)}"
    )

    print(
        f"Requests/level       : "
        f"{REQUESTS_PER_LEVEL}"
    )

    print(
        f"Concurrency levels   : "
        f"{CONCURRENCY_LEVELS}"
    )

    print(
        f"p95 SLO              : "
        f"<= {P95_SLO_MS} ms"
    )

    print(
        f"Error-rate SLO       : "
        f"<= {ERROR_RATE_SLO_PERCENT}%"
    )

    # -----------------------------------------------------------------
    # HEALTH
    # -----------------------------------------------------------------

    print()
    print("Checking service...")

    try:

        health = check_health()

    except Exception as exc:

        raise RuntimeError(
            f"Unable to reach service at "
            f"{HEALTH_URL}: {exc}"
        ) from exc

    print(
        "Health:",
        json.dumps(
            health,
            indent=2,
        ),
    )

    if health.get(
        "status"
    ) != "ok":

        raise RuntimeError(
            "Health check failed."
        )

    if health.get(
        "model_available"
    ) is not True:

        raise RuntimeError(
            "Model is unavailable. "
            "Run the normal load test with "
            "TASK04_MODEL_AVAILABLE=true."
        )

    # -----------------------------------------------------------------
    # WARMUP
    # -----------------------------------------------------------------

    print()

    warmup(
        records
    )

    # -----------------------------------------------------------------
    # CONCURRENCY SWEEP
    # -----------------------------------------------------------------

    print()
    print(
        "Starting concurrency sweep..."
    )
    print("-" * 80)

    experiment_start = (
        time.perf_counter()
    )

    results = []

    for concurrency in CONCURRENCY_LEVELS:

        result = run_load_level(
            concurrency=concurrency,
            requests_per_level=(
                REQUESTS_PER_LEVEL
            ),
            records=records,
        )

        results.append(result)

    experiment_duration_seconds = (
        time.perf_counter()
        - experiment_start
    )

    # -----------------------------------------------------------------
    # BREAKING POINT
    # -----------------------------------------------------------------

    print()
    print(
        "Identifying measured breaking point..."
    )

    breaking_point = identify_breaking_point(
        results
    )

    print(
        json.dumps(
            breaking_point,
            indent=2,
        )
    )

    # -----------------------------------------------------------------
    # HEADROOM
    # -----------------------------------------------------------------

    print()
    print(
        "Calculating operating headroom..."
    )

    headroom = calculate_headroom(
        results,
        breaking_point,
    )

    print(
        json.dumps(
            headroom,
            indent=2,
        )
    )

    # -----------------------------------------------------------------
    # SCALING PLAN
    # -----------------------------------------------------------------

    scaling_plan = build_scaling_plan(
        results,
        breaking_point,
        headroom,
    )

    # -----------------------------------------------------------------
    # LATENCY CURVE
    # -----------------------------------------------------------------

    latency_curve = []

    for item in results:

        latency_curve.append(
            {
                "concurrency": item[
                    "concurrency"
                ],
                "p50_ms": item[
                    "p50_ms"
                ],
                "p95_ms": item[
                    "p95_ms"
                ],
                "p99_ms": item[
                    "p99_ms"
                ],
                "qps": item[
                    "qps"
                ],
                "error_rate_percent": item[
                    "error_rate_percent"
                ],
                "p95_slo_ms": P95_SLO_MS,
                "error_rate_slo_percent": (
                    ERROR_RATE_SLO_PERCENT
                ),
                "overall_slo_pass": item[
                    "overall_slo_pass"
                ],
            }
        )

    # -----------------------------------------------------------------
    # THROUGHPUT
    # -----------------------------------------------------------------

    throughput_results = []

    for item in results:

        throughput_results.append(
            {
                "concurrency": item[
                    "concurrency"
                ],
                "qps": item[
                    "qps"
                ],
                "requests_completed": item[
                    "requests_completed"
                ],
                "requests_failed": item[
                    "requests_failed"
                ],
                "total_requests": item[
                    "total_requests"
                ],
                "error_rate_percent": item[
                    "error_rate_percent"
                ],
            }
        )

    # -----------------------------------------------------------------
    # HIGHEST SAFE LEVEL
    # -----------------------------------------------------------------

    safe_results = [
        item
        for item in results
        if item[
            "overall_slo_pass"
        ]
    ]

    highest_safe = (
        max(
            safe_results,
            key=lambda item: int(
                item["concurrency"]
            ),
        )
        if safe_results
        else None
    )

    highest_safe_concurrency = (
        int(
            highest_safe[
                "concurrency"
            ]
        )
        if highest_safe
        else 0
    )

    maximum_tested_concurrency = max(
        int(
            item["concurrency"]
        )
        for item in results
    )

    # -----------------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------------

    summary = {
        "task": (
            "Phase 3 Task 04 - "
            "Horizontal Scale & Load Readiness"
        ),
        "run_timestamp_utc": now_utc(),
        "service": {
            "url": SERVICE_URL,
            "health_url": HEALTH_URL,
            "health_status": health.get(
                "status"
            ),
            "model_available": health.get(
                "model_available"
            ),
        },
        "dataset": {
            "path": str(DATA_FILE),
            "record_count": len(records),
            "role": (
                "starter/control dataset for "
                "reproducible load testing"
            ),
        },
        "slo": {
            "p95_latency_ms": P95_SLO_MS,
            "error_rate_percent": (
                ERROR_RATE_SLO_PERCENT
            ),
        },
        "experiment": {
            "requests_per_level": (
                REQUESTS_PER_LEVEL
            ),
            "concurrency_levels": (
                CONCURRENCY_LEVELS
            ),
            "warmup_requests": (
                WARMUP_REQUESTS
            ),
            "duration_seconds": round(
                experiment_duration_seconds,
                6,
            ),
        },
        "results": results,
        "highest_safe_concurrency_tested": (
            highest_safe_concurrency
        ),
        "maximum_concurrency_tested": (
            maximum_tested_concurrency
        ),
        "breaking_point": breaking_point,
        "headroom": headroom,
        "scaling_plan": scaling_plan,
        "evidence_boundary": (
            "These measurements represent the "
            "tested local HTTP inference service "
            "and are not production capacity claims."
        ),
    }

    # -----------------------------------------------------------------
    # WRITE EVIDENCE
    # -----------------------------------------------------------------

    print()
    print(
        "Writing evidence artifacts..."
    )

    save_json(
        LOAD_TEST_RESULTS_FILE,
        results,
    )

    save_json(
        LATENCY_CURVE_FILE,
        latency_curve,
    )

    save_json(
        THROUGHPUT_FILE,
        throughput_results,
    )

    save_json(
        BREAKING_POINT_FILE,
        breaking_point,
    )

    save_json(
        HEADROOM_FILE,
        headroom,
    )

    save_json(
        SCALING_PLAN_FILE,
        scaling_plan,
    )

    save_json(
        SUMMARY_FILE,
        summary,
    )

    write_experiment_log(
        results
    )

    # -----------------------------------------------------------------
    # FINAL REPORT
    # -----------------------------------------------------------------

    print_section(
        "TASK 04 LOAD TEST COMPLETE"
    )

    print(
        f"Highest safe concurrency : "
        f"{highest_safe_concurrency}"
    )

    print(
        f"Maximum tested           : "
        f"{maximum_tested_concurrency}"
    )

    if (
        breaking_point.get(
            "status"
        )
        == "BREACH_FOUND"
    ):

        print(
            "Breaking point           : "
            f"{breaking_point.get('breaking_point_concurrency')}"
        )

    else:

        print(
            "Breaking point           : "
            "NOT REACHED IN TESTED RANGE"
        )

    print(
        "Recommended operating    : "
        f"{headroom.get('recommended_operating_concurrency')}"
    )

    print()
    print(
        "Generated evidence:"
    )

    generated_files = [
        LOAD_TEST_RESULTS_FILE,
        LATENCY_CURVE_FILE,
        THROUGHPUT_FILE,
        BREAKING_POINT_FILE,
        HEADROOM_FILE,
        SCALING_PLAN_FILE,
        SUMMARY_FILE,
        EXPERIMENT_LOG_FILE,
    ]

    for path in generated_files:
        print(
            f"  {path}"
        )

    print()
    print(
        "HTTP concurrency experiment completed successfully."
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()