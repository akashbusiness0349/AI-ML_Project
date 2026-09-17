from __future__ import annotations

import json
import statistics
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

BASE_URL = "http://127.0.0.1:8000"
INFER_URL = f"{BASE_URL}/infer"
HEALTH_URL = f"{BASE_URL}/health"

CONCURRENCY_LEVELS = [1, 2, 4, 8, 16, 32, 64, 128]
REQUESTS_PER_LEVEL = 100

LATENCY_SLO_MS = 100.0
ERROR_RATE_SLO = 0.01
AVAILABILITY_SLO = 0.99


def read_json(path: Path, default=None):
    if not path.exists():
        return default

    try:
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            return default

        return json.loads(text)

    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )


def normalize_request(record):
    if not isinstance(record, dict):
        return None

    candidate_skills = (
        record.get("candidate_skills")
        or record.get("skills")
        or record.get("student_skills")
        or record.get("profile_skills")
    )

    required_skills = (
        record.get("required_skills")
        or record.get("job_skills")
        or record.get("target_skills")
        or record.get("requirements")
    )

    if not candidate_skills or not required_skills:
        return None

    if isinstance(candidate_skills, str):
        candidate_skills = [
            x.strip()
            for x in candidate_skills.split(",")
            if x.strip()
        ]

    if isinstance(required_skills, str):
        required_skills = [
            x.strip()
            for x in required_skills.split(",")
            if x.strip()
        ]

    if not isinstance(candidate_skills, list):
        return None

    if not isinstance(required_skills, list):
        return None

    return {
        "student_id": record.get(
            "student_id",
            record.get("id", "task05-load-student"),
        ),
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
    }


def load_requests():
    candidates = [
        (
            DATA_DIR / "inference_requests.json",
            "task05_inference_requests",
        ),
        (
            ROOT.parent / "task04" / "data" / "inference_requests.json",
            "task04_control_requests",
        ),
        (
            DATA_DIR / "heldout_validation.json",
            "task05_heldout_validation",
        ),
    ]

    for path, source_name in candidates:
        raw = read_json(path, None)

        if isinstance(raw, dict):
            raw = (
                raw.get("records")
                or raw.get("requests")
                or raw.get("data")
                or []
            )

        if not isinstance(raw, list):
            continue

        requests = []

        for record in raw:
            normalized = normalize_request(record)

            if normalized:
                requests.append(normalized)

        if requests:
            print(
                f"Load-test data source : {source_name}"
            )
            print(
                f"Usable request records : {len(requests)}"
            )

            # Keep a copy inside Task 05 so the evidence is reproducible.
            write_json(
                DATA_DIR / "inference_requests.json",
                {
                    "source": source_name,
                    "record_count": len(requests),
                    "records": requests,
                },
            )

            return requests

    raise RuntimeError(
        "No usable load-test request records found. "
        "Expected candidate_skills and required_skills in "
        "Task 05, Task 04, or held-out validation data."
    )


def percentile(values, p):
    if not values:
        return 0.0

    values = sorted(values)

    index = (len(values) - 1) * (p / 100.0)

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    fraction = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


def send_request(request):
    started = time.perf_counter()

    payload = json.dumps(request).encode("utf-8")

    http_request = urllib.request.Request(
        INFER_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            http_request,
            timeout=10,
        ) as response:

            body = response.read().decode("utf-8")

            elapsed_ms = (
                time.perf_counter() - started
            ) * 1000.0

            status_code = response.status

            try:
                result = json.loads(body)
            except json.JSONDecodeError:
                result = {}

            model_unavailable = (
                result.get("status") == "MODEL_UNAVAILABLE"
            )

            return {
                "latency_ms": elapsed_ms,
                "status_code": status_code,
                "success": not model_unavailable
                and 200 <= status_code < 300,
                "fallback": model_unavailable,
            }

    except Exception as exc:
        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000.0

        return {
            "latency_ms": elapsed_ms,
            "status_code": None,
            "success": False,
            "fallback": False,
            "error": str(exc),
        }


def run_level(requests, concurrency):
    total_requests = REQUESTS_PER_LEVEL

    latencies = []
    errors = 0
    fallbacks = 0

    started = time.perf_counter()

    work = [
        requests[i % len(requests)]
        for i in range(total_requests)
    ]

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = [
            executor.submit(send_request, request)
            for request in work
        ]

        for future in as_completed(futures):
            result = future.result()

            latencies.append(result["latency_ms"])

            if not result["success"]:
                errors += 1

            if result["fallback"]:
                fallbacks += 1

    elapsed_seconds = time.perf_counter() - started

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    qps = (
        total_requests / elapsed_seconds
        if elapsed_seconds > 0
        else 0.0
    )

    error_rate = errors / total_requests

    availability = 1.0 - error_rate

    passed = (
        p95 <= LATENCY_SLO_MS
        and error_rate <= ERROR_RATE_SLO
        and availability >= AVAILABILITY_SLO
    )

    return {
        "concurrency": concurrency,
        "requests": total_requests,
        "duration_seconds": round(
            elapsed_seconds,
            6,
        ),
        "p50_ms": round(p50, 6),
        "p95_ms": round(p95, 6),
        "p99_ms": round(p99, 6),
        "qps": round(qps, 6),
        "errors": errors,
        "error_rate": round(
            error_rate,
            6,
        ),
        "availability": round(
            availability,
            6,
        ),
        "fallbacks": fallbacks,
        "slo_latency_ms": LATENCY_SLO_MS,
        "slo_error_rate": ERROR_RATE_SLO,
        "slo_availability": AVAILABILITY_SLO,
        "passed": passed,
    }


def check_health():
    with urllib.request.urlopen(
        HEALTH_URL,
        timeout=5,
    ) as response:

        body = response.read().decode("utf-8")

        print(
            "Health:",
            body,
        )


def main():
    print("=" * 80)
    print("PHASE 3 / TASK 05")
    print("RELIABILITY SIGN-OFF & SCALE INTEGRATION")
    print("=" * 80)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    check_health()

    requests = load_requests()

    print()
    print("Latency SLO :", LATENCY_SLO_MS, "ms")
    print("Availability SLO :", AVAILABILITY_SLO)
    print("Error-rate SLO :", ERROR_RATE_SLO)
    print()
    print("Running concurrency sweep...")
    print()

    results = []

    for concurrency in CONCURRENCY_LEVELS:
        print(
            f"[concurrency={concurrency}] "
            f"running {REQUESTS_PER_LEVEL} requests..."
        )

        result = run_level(
            requests,
            concurrency,
        )

        results.append(result)

        print(
            f"  p50={result['p50_ms']:.3f} ms | "
            f"p95={result['p95_ms']:.3f} ms | "
            f"p99={result['p99_ms']:.3f} ms | "
            f"QPS={result['qps']:.3f} | "
            f"errors={result['errors']} | "
            f"PASS={result['passed']}"
        )

    safe_results = [
        result
        for result in results
        if result["passed"]
    ]

    if safe_results:
        highest_safe = max(
            safe_results,
            key=lambda x: x["concurrency"],
        )

        highest_safe_concurrency = (
            highest_safe["concurrency"]
        )

        recommended_concurrency = max(
            1,
            int(
                highest_safe_concurrency * 0.70
            ),
        )

    else:
        highest_safe_concurrency = 0
        recommended_concurrency = 0

    breached = [
        result
        for result in results
        if not result["passed"]
    ]

    if breached:
        breaking_point = min(
            breached,
            key=lambda x: x["concurrency"],
        )

        breaking_point_concurrency = (
            breaking_point["concurrency"]
        )

    else:
        breaking_point_concurrency = None

    load_results = {
        "task": "phase3_task05",
        "service": "task05-reliability-service",
        "base_url": BASE_URL,
        "request_source": (
            read_json(
                DATA_DIR / "inference_requests.json",
                {},
            ).get(
                "source",
                "unknown",
            )
        ),
        "requests_per_level": REQUESTS_PER_LEVEL,
        "concurrency_levels": CONCURRENCY_LEVELS,
        "slo": {
            "p95_latency_ms": LATENCY_SLO_MS,
            "error_rate": ERROR_RATE_SLO,
            "availability": AVAILABILITY_SLO,
        },
        "results": results,
        "highest_safe_tested_concurrency": (
            highest_safe_concurrency
        ),
        "recommended_operating_concurrency": (
            recommended_concurrency
        ),
        "breaking_point_concurrency": (
            breaking_point_concurrency
        ),
        "generated_at_epoch": time.time(),
    }

    write_json(
        LOG_DIR / "load_test_results.json",
        load_results,
    )

    write_json(
        LOG_DIR / "latency_curve.json",
        {
            "points": [
                {
                    "concurrency": x["concurrency"],
                    "p50_ms": x["p50_ms"],
                    "p95_ms": x["p95_ms"],
                    "p99_ms": x["p99_ms"],
                }
                for x in results
            ]
        },
    )

    write_json(
        LOG_DIR / "slo_results.json",
        {
            "slo": load_results["slo"],
            "results": results,
            "all_levels_within_slo": all(
                x["passed"]
                for x in results
            ),
            "highest_safe_tested_concurrency": (
                highest_safe_concurrency
            ),
            "breaking_point_concurrency": (
                breaking_point_concurrency
            ),
        },
    )

    headroom_target = 0.30

    if highest_safe_concurrency:
        capacity_reference = (
            highest_safe_concurrency
        )

        target_headroom_concurrency = (
            capacity_reference
            * (1.0 - headroom_target)
        )

        recommended = max(
            1,
            int(target_headroom_concurrency),
        )

        headroom = {
            "capacity_reference_concurrency": capacity_reference,
            "headroom_target": headroom_target,
            "target_operating_concurrency": round(
                target_headroom_concurrency,
                3,
            ),
            "recommended_operating_concurrency": recommended,
            "headroom_policy": (
                "Operate below the highest tested "
                "SLO-safe concurrency and reserve "
                "30% capacity headroom."
            ),
        }

    else:
        headroom = {
            "capacity_reference_concurrency": 0,
            "headroom_target": headroom_target,
            "target_operating_concurrency": 0,
            "recommended_operating_concurrency": 0,
            "headroom_policy": (
                "No safe concurrency was established."
            ),
        }

    write_json(
        LOG_DIR / "headroom_analysis.json",
        headroom,
    )

    write_json(
        LOG_DIR / "breaking_point.json",
        {
            "breaking_point_concurrency": (
                breaking_point_concurrency
            ),
            "highest_safe_tested_concurrency": (
                highest_safe_concurrency
            ),
            "reason": (
                "First tested concurrency level "
                "where one or more reliability SLOs "
                "were breached."
            ),
        },
    )

    write_json(
        LOG_DIR / "monitoring_results.json",
        {
            "service_health_checked": True,
            "load_test_completed": True,
            "metrics": [
                "p50_ms",
                "p95_ms",
                "p99_ms",
                "qps",
                "error_rate",
                "availability",
                "fallbacks",
            ],
            "slo_monitored": True,
        },
    )

    write_json(
        LOG_DIR / "throughput_results.json",
        {
            "results": [
                {
                    "concurrency": x["concurrency"],
                    "qps": x["qps"],
                    "errors": x["errors"],
                }
                for x in results
            ]
        },
    )

    with open(
        LOG_DIR / "experiment_log.csv",
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(
            "concurrency,requests,p50_ms,p95_ms,"
            "p99_ms,qps,error_rate,availability,"
            "passed\n"
        )

        for result in results:
            handle.write(
                f"{result['concurrency']},"
                f"{result['requests']},"
                f"{result['p50_ms']},"
                f"{result['p95_ms']},"
                f"{result['p99_ms']},"
                f"{result['qps']},"
                f"{result['error_rate']},"
                f"{result['availability']},"
                f"{result['passed']}\n"
            )

    print()
    print("=" * 80)
    print("LOAD TEST COMPLETE")
    print("=" * 80)
    print(
        "Highest safe tested concurrency :",
        highest_safe_concurrency,
    )
    print(
        "Recommended operating concurrency :",
        recommended_concurrency,
    )
    print(
        "Breaking point concurrency :",
        breaking_point_concurrency,
    )
    print(
        "Evidence written :",
        LOG_DIR / "load_test_results.json",
    )


if __name__ == "__main__":
    main()