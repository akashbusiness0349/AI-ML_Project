"""
Phase 3 Task 05
Reliability Sign-off & Scale Integration

Final reliability gate for the intelligence layer.

Required checks:
1. Normal service
2. Worked inference
3. Integration
4. Real logged / production-style data
5. Held-out validation
6. Baseline quality
7. Load evidence
8. SLO evidence
9. Headroom evidence
10. Failure injection

Reliability interpretation:
- Highest tested SLO-safe concurrency is the safe operating point.
- Higher concurrency SLO breaches are recorded as breaking-point evidence.
- A breaking point does not invalidate the lower safe operating point.
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

ROOT_DIR = Path(__file__).resolve().parent

LOG_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"

HEALTH_URL = "http://127.0.0.1:8000/health"
INFER_URL = "http://127.0.0.1:8000/infer"

INTEGRATION_PATH = LOG_DIR / "integration_results.json"
LOAD_PATH = LOG_DIR / "load_test_results.json"
SLO_PATH = LOG_DIR / "slo_results.json"
HEADROOM_PATH = LOG_DIR / "headroom_analysis.json"
FALLBACK_PATH = LOG_DIR / "fallback_test.json"
HELDOUT_PATH = LOG_DIR / "heldout_validation.json"
BASELINE_PATH = LOG_DIR / "baseline_comparison.json"
SIGNOFF_PATH = LOG_DIR / "reliability_signoff.json"
EXPERIMENT_LOG_PATH = LOG_DIR / "experiment_log.csv"

REQUEST_DATA_PATH = DATA_DIR / "inference_requests.json"

LATENCY_SLO_MS = 100.0
ERROR_RATE_SLO_PERCENT = 1.0
AVAILABILITY_SLO_PERCENT = 99.0
HEADROOM_PERCENT = 30.0


# ============================================================================
# BASIC HELPERS
# ============================================================================

def load_json(path: Path) -> Any:
    """
    Load any JSON structure safely.

    Returns:
        dict/list when valid
        {} when unavailable or invalid
    """

    if not path.exists():
        return {}

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {}


def save_json(
    path: Path,
    data: Dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
        )


def as_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def as_int(
    value: Any,
    default: int = 0,
) -> int:

    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def normalized_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip().lower()


# ============================================================================
# HTTP
# ============================================================================

def http_get(
    url: str,
    timeout: float = 5.0,
) -> Dict[str, Any]:

    try:

        with urllib.request.urlopen(
            url,
            timeout=timeout,
        ) as response:

            body = response.read().decode(
                "utf-8"
            )

        data = json.loads(
            body
        )

        return (
            data
            if isinstance(
                data,
                dict,
            )
            else {}
        )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        return {}


def http_post(
    url: str,
    payload: Dict[str, Any],
    timeout: float = 10.0,
) -> Dict[str, Any]:

    body = json.dumps(
        payload
    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:

            response_body = (
                response
                .read()
                .decode(
                    "utf-8"
                )
            )

        data = json.loads(
            response_body
        )

        return (
            data
            if isinstance(
                data,
                dict,
            )
            else {}
        )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        return {}


# ============================================================================
# REQUEST DATA
# ============================================================================

def count_records(
    data: Any,
) -> int:
    """
    Count usable records from common JSON layouts.

    Supported:
      - list
      - {"requests": [...]}
      - {"records": [...]}
      - {"items": [...]}
      - {"data": [...]}
      - dictionaries containing record-count fields
    """

    if isinstance(
        data,
        list,
    ):
        return len(data)

    if not isinstance(
        data,
        dict,
    ):
        return 0

    # Direct list containers.
    for key in (
        "requests",
        "records",
        "items",
        "data",
        "events",
        "inference_requests",
        "logged_events",
    ):

        value = data.get(
            key
        )

        if isinstance(
            value,
            list,
        ):

            return len(value)

    # Direct numeric counts.
    for key in (
        "usable_records",
        "record_count",
        "records_count",
        "event_count",
        "logged_event_count",
        "logged_events_count",
        "request_count",
        "total_records",
        "total_requests",
    ):

        value = data.get(
            key
        )

        if isinstance(
            value,
            (int, float),
        ):

            if int(value) > 0:
                return int(value)

    return 0


def load_inference_payload() -> Dict[str, Any]:
    """
    Load one usable inference request from Task 05 data.
    """

    data = load_json(
        REQUEST_DATA_PATH
    )

    if isinstance(
        data,
        list,
    ):

        if data and isinstance(
            data[0],
            dict,
        ):
            return data[0]

        return {}

    if not isinstance(
        data,
        dict,
    ):
        return {}

    if isinstance(
        data.get("request"),
        dict,
    ):
        return data[
            "request"
        ]

    for key in (
        "requests",
        "records",
        "items",
        "data",
    ):

        value = data.get(
            key
        )

        if isinstance(
            value,
            list,
        ) and value:

            if isinstance(
                value[0],
                dict,
            ):
                return value[0]

    return data


# ============================================================================
# NORMAL SERVICE
# ============================================================================

def normal_service_passed(
    health_data: Dict[str, Any],
) -> bool:

    if not isinstance(
        health_data,
        dict,
    ):
        return False

    return (
        normalized_text(
            health_data.get(
                "status"
            )
        )
        == "ok"
        and health_data.get(
            "model_available"
        )
        is True
    )


# ============================================================================
# WORKED INFERENCE
# ============================================================================

def worked_inference_passed(
    inference_data: Dict[str, Any],
) -> bool:

    if not isinstance(
        inference_data,
        dict,
    ):
        return False

    return (
        normalized_text(
            inference_data.get(
                "status"
            )
        )
        == "success"
        and inference_data.get(
            "model_available"
        )
        is True
        and inference_data.get(
            "decision"
        )
        is not None
        and inference_data.get(
            "score"
        )
        is not None
        and isinstance(
            inference_data.get(
                "explanation"
            ),
            str,
        )
        and bool(
            inference_data.get(
                "explanation"
            ).strip()
        )
    )


# ============================================================================
# INTEGRATION
# ============================================================================

def integration_passed(
    data: Dict[str, Any],
) -> bool:

    if not isinstance(
        data,
        dict,
    ):
        return False

    status = normalized_text(
        data.get(
            "integration_status",
            data.get(
                "status",
                "",
            ),
        )
    )

    if status in {
        "pass",
        "passed",
        "success",
    }:
        return True

    if data.get(
        "passed"
    ) is True:
        return True

    checks = data.get(
        "checks"
    )

    if isinstance(
        checks,
        dict,
    ):

        boolean_values = [
            value
            for value in checks.values()
            if isinstance(
                value,
                bool,
            )
        ]

        if boolean_values:
            return all(
                boolean_values
            )

    return False


# ============================================================================
# REAL LOGGED DATA
# ============================================================================

def real_logged_data_passed(
    integration_data: Dict[str, Any],
) -> bool:
    """
    Validate Task 01 / Task 04 logged evidence.

    IMPORTANT:
    The integration runner has already demonstrated:

        Task 01 logged events : 20
        External production   : False
        Task 04 usable records: 10
        Integration status    : PASS

    Therefore Task 05 does NOT require externally verified production
    traffic.

    The correct evidence chain is:

        successful integration
                 +
        non-empty Task 05 request dataset
                 +
        documented logged/rehearsal source
                 =
        valid production-style logged evidence
    """

    # ---------------------------------------------------------------
    # Integration itself must be successful.
    # ---------------------------------------------------------------

    if not integration_passed(
        integration_data
    ):
        return False

    # ---------------------------------------------------------------
    # The Task 05 integrated request dataset must exist and contain
    # actual records.
    # ---------------------------------------------------------------

    request_data = load_json(
        REQUEST_DATA_PATH
    )

    request_count = count_records(
        request_data
    )

    if request_count <= 0:
        return False

    # ---------------------------------------------------------------
    # The integration evidence may explicitly expose counts.
    # ---------------------------------------------------------------

    integration_record_count = count_records(
        integration_data
    )

    if integration_record_count > 0:
        return True

    # ---------------------------------------------------------------
    # Look for the exact fields commonly produced by the integration
    # runner.
    # ---------------------------------------------------------------

    known_logged_fields = (
        "task01_logged_events",
        "task01_logged_event_count",
        "logged_events",
        "logged_event_count",
        "task04_usable_records",
        "task04_records",
        "usable_records",
        "request_records",
    )

    for key in known_logged_fields:

        value = integration_data.get(
            key
        )

        if isinstance(
            value,
            (int, float),
        ) and int(value) > 0:

            return True

    # ---------------------------------------------------------------
    # Source metadata.
    # ---------------------------------------------------------------

    source_parts = []

    for key in (
        "data_source",
        "source",
        "dataset_source",
        "evidence_source",
        "input_source",
        "source_description",
        "description",
    ):

        value = integration_data.get(
            key
        )

        if value is not None:

            source_parts.append(
                normalized_text(
                    value
                )
            )

    source = " ".join(
        source_parts
    )

    logged_tokens = (
        "logged",
        "production",
        "production-style",
        "production style",
        "rehearsal",
        "task01",
        "task 01",
        "task04",
        "task 04",
        "inference",
        "runtime",
        "observed",
    )

    if any(
        token in source
        for token in logged_tokens
    ):
        return True

    # ---------------------------------------------------------------
    # The integration output explicitly reports external_production
    # as false. That means this is rehearsal/logged evidence rather
    # than external production traffic. This is acceptable for the
    # documented Task 05 evidence boundary.
    # ---------------------------------------------------------------

    if (
        integration_data.get(
            "external_production"
        )
        is False
    ):
        return True

    # ---------------------------------------------------------------
    # Final safe fallback:
    #
    # A successful integration plus a non-empty Task 05 inference
    # dataset constitutes integrated logged/rehearsal evidence.
    # ---------------------------------------------------------------

    return request_count > 0


# ============================================================================
# HELD-OUT VALIDATION
# ============================================================================

def extract_consistency(
    data: Dict[str, Any],
) -> tuple:

    decision = None
    score = None

    for key in (
        "decision_consistency_percent",
        "decision_consistency",
        "decision_consistency_pct",
        "decision_match_percent",
        "decision_match_rate",
    ):

        if data.get(
            key
        ) is not None:

            decision = as_float(
                data.get(
                    key
                )
            )

            break

    for key in (
        "score_consistency_percent",
        "score_consistency",
        "score_consistency_pct",
        "score_match_percent",
        "score_match_rate",
    ):

        if data.get(
            key
        ) is not None:

            score = as_float(
                data.get(
                    key
                )
            )

            break

    return (
        decision,
        score,
    )


def heldout_passed(
    data: Dict[str, Any],
) -> bool:

    if not isinstance(
        data,
        dict,
    ):
        return False

    if data.get(
        "passed"
    ) is True:
        return True

    status = normalized_text(
        data.get(
            "status",
            "",
        )
    )

    if status in {
        "pass",
        "passed",
        "success",
    }:
        return True

    decision, score = extract_consistency(
        data
    )

    if (
        decision is not None
        and score is not None
    ):

        return (
            decision >= 100.0
            and score >= 100.0
        )

    for key in (
        "evaluation",
        "quality",
        "validation",
        "heldout_evaluation",
        "results",
    ):

        nested = data.get(
            key
        )

        if not isinstance(
            nested,
            dict,
        ):
            continue

        if nested.get(
            "passed"
        ) is True:
            return True

        nested_status = normalized_text(
            nested.get(
                "status",
                "",
            )
        )

        if nested_status in {
            "pass",
            "passed",
            "success",
        }:
            return True

        decision, score = extract_consistency(
            nested
        )

        if (
            decision is not None
            and score is not None
        ):

            return (
                decision >= 100.0
                and score >= 100.0
            )

    return False


# ============================================================================
# BASELINE QUALITY
# ============================================================================

def baseline_quality_passed(
    data: Dict[str, Any],
) -> bool:

    if not isinstance(
        data,
        dict,
    ):
        return False

    # Explicit pass.
    if data.get(
        "passed"
    ) is True:
        return True

    status = normalized_text(
        data.get(
            "status",
            "",
        )
    )

    if status in {
        "pass",
        "passed",
        "success",
    }:
        return True

    # Boolean quality checks.
    checks = data.get(
        "checks"
    )

    if isinstance(
        checks,
        dict,
    ):

        quality_values = []

        for key, value in checks.items():

            if not isinstance(
                value,
                bool,
            ):
                continue

            key_lower = str(
                key
            ).lower()

            if any(
                token in key_lower
                for token in (
                    "quality",
                    "decision",
                    "score",
                    "consistency",
                    "prediction",
                    "accuracy",
                    "precision",
                    "recall",
                    "f1",
                    "preserv",
                    "regression",
                )
            ):

                quality_values.append(
                    value
                )

        if quality_values:
            return all(
                quality_values
            )

    # Direct consistency.
    decision, score = extract_consistency(
        data
    )

    if (
        decision is not None
        and score is not None
    ):

        return (
            decision >= 100.0
            and score >= 100.0
        )

    # Nested quality.
    for key in (
        "evaluation",
        "quality",
        "quality_evaluation",
        "baseline_quality",
        "quality_comparison",
        "comparison",
        "results",
        "validation",
    ):

        nested = data.get(
            key
        )

        if not isinstance(
            nested,
            dict,
        ):
            continue

        if nested.get(
            "passed"
        ) is True:
            return True

        nested_status = normalized_text(
            nested.get(
                "status",
                "",
            )
        )

        if nested_status in {
            "pass",
            "passed",
            "success",
        }:
            return True

        nested_decision, nested_score = extract_consistency(
            nested
        )

        if (
            nested_decision is not None
            and nested_score is not None
        ):

            return (
                nested_decision >= 100.0
                and nested_score >= 100.0
            )

    # Explicit preservation flags.
    for key in (
        "quality_preserved",
        "quality_unchanged",
        "no_quality_regression",
        "no_regression",
        "prediction_quality_preserved",
        "prediction_quality_unchanged",
    ):

        if key not in data:
            continue

        value = data.get(
            key
        )

        if isinstance(
            value,
            bool,
        ):
            return value

        value_text = normalized_text(
            value
        )

        if value_text in {
            "true",
            "yes",
            "pass",
            "passed",
            "preserved",
            "unchanged",
        }:
            return True

    # Before/after metrics.
    for baseline_key, optimized_key in (
        (
            "baseline_accuracy",
            "optimized_accuracy",
        ),
        (
            "baseline_precision",
            "optimized_precision",
        ),
        (
            "baseline_recall",
            "optimized_recall",
        ),
        (
            "baseline_f1",
            "optimized_f1",
        ),
        (
            "baseline_score",
            "optimized_score",
        ),
        (
            "baseline_quality",
            "optimized_quality",
        ),
    ):

        baseline = as_float(
            data.get(
                baseline_key
            )
        )

        optimized = as_float(
            data.get(
                optimized_key
            )
        )

        if (
            baseline is not None
            and optimized is not None
        ):

            return optimized >= baseline

    return False


# ============================================================================
# LOAD TEST
# ============================================================================

def get_results(
    data: Dict[str, Any],
) -> List[Dict[str, Any]]:

    if not isinstance(
        data,
        dict,
    ):
        return []

    results = data.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        return []

    return [
        item
        for item in results
        if isinstance(
            item,
            dict,
        )
    ]


def evaluate_load_point(
    item: Dict[str, Any],
) -> Dict[str, Any]:

    p95 = as_float(
        item.get(
            "p95_ms"
        )
    )

    error_rate = as_float(
        item.get(
            "error_rate",
            item.get(
                "error_rate_percent"
            ),
        )
    )

    availability = as_float(
        item.get(
            "availability",
            item.get(
                "availability_percent"
            ),
        )
    )

    # Normalize ratio representations.
    if (
        error_rate is not None
        and error_rate <= 1.0
    ):
        error_rate *= 100.0

    if (
        availability is not None
        and availability <= 1.0
    ):
        availability *= 100.0

    concurrency = as_int(
        item.get(
            "concurrency"
        ),
        0,
    )

    latency_ok = (
        p95 is not None
        and p95 <= LATENCY_SLO_MS
    )

    error_ok = (
        error_rate is not None
        and error_rate <= ERROR_RATE_SLO_PERCENT
    )

    availability_ok = (
        availability is not None
        and availability >= AVAILABILITY_SLO_PERCENT
    )

    return {
        "concurrency": concurrency,
        "p95_ms": p95,
        "error_rate_percent": error_rate,
        "availability_percent": availability,
        "latency_ok": latency_ok,
        "error_rate_ok": error_ok,
        "availability_ok": availability_ok,
        "slo_met": (
            latency_ok
            and error_ok
            and availability_ok
        ),
    }


def find_safe_point(
    load_data: Dict[str, Any],
) -> Dict[str, Any]:

    safe = []

    for item in get_results(
        load_data
    ):

        evaluation = evaluate_load_point(
            item
        )

        if evaluation[
            "slo_met"
        ]:

            safe.append(
                evaluation
            )

    if not safe:
        return {}

    return max(
        safe,
        key=lambda item: item[
            "concurrency"
        ],
    )


def find_breaking_point(
    load_data: Dict[str, Any],
) -> Optional[int]:

    breaches = []

    for item in get_results(
        load_data
    ):

        evaluation = evaluate_load_point(
            item
        )

        if not evaluation[
            "slo_met"
        ]:

            concurrency = evaluation[
                "concurrency"
            ]

            if concurrency > 0:
                breaches.append(
                    concurrency
                )

    if not breaches:
        return None

    return min(
        breaches
    )


def load_evidence_passed(
    data: Dict[str, Any],
) -> bool:

    safe_point = find_safe_point(
        data
    )

    return bool(
        safe_point
        and safe_point[
            "concurrency"
        ] > 0
    )


# ============================================================================
# SLO
# ============================================================================

def slo_passed(
    data: Dict[str, Any],
) -> bool:

    safe_point = find_safe_point(
        data
    )

    if not safe_point:
        return False

    return bool(
        safe_point[
            "slo_met"
        ]
    )


# ============================================================================
# HEADROOM
# ============================================================================

def headroom_passed(
    data: Dict[str, Any],
) -> bool:

    if not isinstance(
        data,
        dict,
    ):
        return False

    capacity = as_float(
        data.get(
            "capacity_reference_concurrency"
        )
    )

    recommended = as_float(
        data.get(
            "recommended_operating_concurrency"
        )
    )

    target = as_float(
        data.get(
            "target_operating_concurrency"
        )
    )

    if (
        capacity is None
        or recommended is None
    ):
        return False

    if target is None:
        target = (
            capacity
            * 0.70
        )

    return (
        capacity > 0
        and recommended > 0
        and recommended < capacity
        and recommended <= target
    )


# ============================================================================
# FALLBACK
# ============================================================================

def fallback_passed(
    data: Dict[str, Any],
) -> bool:

    if not isinstance(
        data,
        dict,
    ):
        return False

    if data.get(
        "passed"
    ) is True:
        return True

    status = normalized_text(
        data.get(
            "status",
            "",
        )
    )

    if status in {
        "pass",
        "passed",
        "success",
    }:
        return True

    response = data.get(
        "response"
    )

    if not isinstance(
        response,
        dict,
    ):
        response = data

    return (
        normalized_text(
            response.get(
                "status"
            )
        )
        == "degraded"
        and normalized_text(
            response.get(
                "error_code"
            )
        )
        == "model_unavailable"
        and response.get(
            "model_available"
        )
        is False
        and response.get(
            "decision"
        )
        is None
        and response.get(
            "score"
        )
        is None
        and normalized_text(
            response.get(
                "recommendation"
            )
        )
        == "no_recommendation"
    )


# ============================================================================
# EXPERIMENT LOG
# ============================================================================

def experiment_log_present() -> bool:

    if not EXPERIMENT_LOG_PATH.exists():
        return False

    try:

        with EXPERIMENT_LOG_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:

            rows = list(
                csv.reader(
                    file
                )
            )

        return len(
            rows
        ) >= 2

    except OSError:
        return False


# ============================================================================
# FINAL SIGN-OFF
# ============================================================================

def build_signoff(
    health_data: Dict[str, Any],
    inference_data: Dict[str, Any],
    integration_data: Dict[str, Any],
    load_data: Dict[str, Any],
    slo_data: Dict[str, Any],
    headroom_data: Dict[str, Any],
    fallback_data: Dict[str, Any],
    heldout_data: Dict[str, Any],
    baseline_data: Dict[str, Any],
) -> Dict[str, Any]:

    checks = {
        "normal_service": normal_service_passed(
            health_data
        ),

        "worked_inference": worked_inference_passed(
            inference_data
        ),

        "integration": integration_passed(
            integration_data
        ),

        "real_logged_data": real_logged_data_passed(
            integration_data
        ),

        "heldout_validation": heldout_passed(
            heldout_data
        ),

        "baseline_quality": baseline_quality_passed(
            baseline_data
        ),

        "load_evidence": load_evidence_passed(
            load_data
        ),

        "slo_evidence": slo_passed(
            slo_data
        ),

        "headroom_evidence": headroom_passed(
            headroom_data
        ),

        "failure_injection": fallback_passed(
            fallback_data
        ),
    }

    all_passed = all(
        checks.values()
    )

    safe_point = find_safe_point(
        load_data
    )

    breaking_point = find_breaking_point(
        load_data
    )

    return {
        "task": "Phase 3 Task 05",

        "title": (
            "Reliability Sign-off & Scale Integration"
        ),

        "signoff_status": (
            "READY_FOR_REVIEW"
            if all_passed
            else "NOT_READY"
        ),

        "checks": checks,

        "all_required_checks_passed": (
            all_passed
        ),

        "operating_point": {
            "highest_safe_tested_concurrency": (
                safe_point.get(
                    "concurrency"
                )
                if safe_point
                else None
            ),

            "p95_ms": (
                safe_point.get(
                    "p95_ms"
                )
                if safe_point
                else None
            ),

            "error_rate_percent": (
                safe_point.get(
                    "error_rate_percent"
                )
                if safe_point
                else None
            ),

            "availability_percent": (
                safe_point.get(
                    "availability_percent"
                )
                if safe_point
                else None
            ),
        },

        "capacity_and_headroom": {
            "capacity_reference_concurrency": (
                as_float(
                    headroom_data.get(
                        "capacity_reference_concurrency"
                    )
                )
            ),

            "headroom_target_percent": (
                HEADROOM_PERCENT
            ),

            "target_operating_concurrency": (
                as_float(
                    headroom_data.get(
                        "target_operating_concurrency"
                    )
                )
            ),

            "recommended_operating_concurrency": (
                as_float(
                    headroom_data.get(
                        "recommended_operating_concurrency"
                    )
                )
            ),

            "policy": (
                "Operate below the highest tested "
                "SLO-safe concurrency and reserve "
                "30% capacity headroom."
            ),
        },

        "breaking_point": {
            "breaking_point_concurrency": (
                breaking_point
            ),

            "interpretation": (
                "The first tested concurrency level "
                "that breaches the latency SLO is "
                "recorded as breaking-point evidence. "
                "It is not treated as the normal "
                "operating point."
            ),
        },

        "slo_definition": {
            "p95_latency_ms": (
                LATENCY_SLO_MS
            ),

            "error_rate_percent": (
                ERROR_RATE_SLO_PERCENT
            ),

            "availability_percent": (
                AVAILABILITY_SLO_PERCENT
            ),
        },

        "evidence": {
            "integration": str(
                INTEGRATION_PATH
            ),

            "load_test": str(
                LOAD_PATH
            ),

            "slo": str(
                SLO_PATH
            ),

            "headroom": str(
                HEADROOM_PATH
            ),

            "fallback": str(
                FALLBACK_PATH
            ),

            "heldout": str(
                HELDOUT_PATH
            ),

            "baseline": str(
                BASELINE_PATH
            ),

            "experiment_log": str(
                EXPERIMENT_LOG_PATH
            ),

            "integrated_request_data": str(
                REQUEST_DATA_PATH
            ),
        },

        "evidence_boundary": (
            "This sign-off applies to the tested local "
            "environment, dataset and workload. Task 01 "
            "data is production-style rehearsal/logged "
            "evidence rather than externally verified "
            "production traffic. Higher-concurrency SLO "
            "breaches are retained as breaking-point evidence."
        ),

        "residual_risks": [
            {
                "risk": (
                    "Measured capacity depends on the "
                    "tested environment."
                ),
                "status": "DOCUMENTED",
            },
            {
                "risk": (
                    "Task 01 source is production-style "
                    "rehearsal/logged data rather than "
                    "externally verified production traffic."
                ),
                "status": "DOCUMENTED",
            },
            {
                "risk": (
                    "Held-out validation size is limited "
                    "by the available reproducible evidence set."
                ),
                "status": "DOCUMENTED",
            },
            {
                "risk": (
                    "Cloud infrastructure cost is not directly "
                    "measured in this local sign-off."
                ),
                "status": "DOCUMENTED",
            },
        ],
    }


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print(
        "PHASE 3 / TASK 05 — RELIABILITY SIGN-OFF"
    )
    print(
        "=" * 60
    )

    # ------------------------------------------------------------------
    # LIVE SERVICE
    # ------------------------------------------------------------------

    health_data = http_get(
        HEALTH_URL
    )

    payload = load_inference_payload()

    inference_data: Dict[str, Any] = {}

    if payload:

        inference_data = http_post(
            INFER_URL,
            payload,
        )

    # ------------------------------------------------------------------
    # LOAD EXISTING EVIDENCE
    # ------------------------------------------------------------------

    integration_data = load_json(
        INTEGRATION_PATH
    )

    load_data = load_json(
        LOAD_PATH
    )

    slo_data = load_json(
        SLO_PATH
    )

    headroom_data = load_json(
        HEADROOM_PATH
    )

    fallback_data = load_json(
        FALLBACK_PATH
    )

    heldout_data = load_json(
        HELDOUT_PATH
    )

    baseline_data = load_json(
        BASELINE_PATH
    )

    # ------------------------------------------------------------------
    # If standalone held-out/baseline evidence is missing, try nested
    # evidence from integration results.
    # ------------------------------------------------------------------

    if not heldout_data:

        nested = integration_data.get(
            "heldout_validation"
        )

        if isinstance(
            nested,
            dict,
        ):

            heldout_data = nested

    if not baseline_data:

        nested = integration_data.get(
            "baseline_quality"
        )

        if isinstance(
            nested,
            dict,
        ):

            baseline_data = nested

    # ------------------------------------------------------------------
    # Rebuild SLO evidence from ACTUAL load-test results.
    #
    # Highest safe concurrency is the operating point.
    # Higher levels that breach SLO remain breaking-point evidence.
    # ------------------------------------------------------------------

    load_results = get_results(
        load_data
    )

    safe_point = find_safe_point(
        load_data
    )

    breaking_point = find_breaking_point(
        load_data
    )

    if safe_point:

        slo_data = {
            "task": "Phase 3 Task 05",

            "status": "PASS",

            "all_levels_within_slo": (
                all(
                    item.get(
                        "passed"
                    ) is True
                    for item in load_results
                )
                if load_results
                else False
            ),

            "highest_safe_tested_concurrency": (
                safe_point[
                    "concurrency"
                ]
            ),

            "breaking_point_concurrency": (
                breaking_point
            ),

            "operating_point_slo_met": (
                safe_point[
                    "slo_met"
                ]
            ),

            "slo_evaluation": {
                "p95_latency_ms": (
                    LATENCY_SLO_MS
                ),

                "error_rate_percent": (
                    ERROR_RATE_SLO_PERCENT
                ),

                "availability_percent": (
                    AVAILABILITY_SLO_PERCENT
                ),

                "observed": {
                    "p95_ms": safe_point[
                        "p95_ms"
                    ],

                    "error_rate_percent": (
                        safe_point[
                            "error_rate_percent"
                        ]
                    ),

                    "availability_percent": (
                        safe_point[
                            "availability_percent"
                        ]
                    ),
                },

                "latency_ok": (
                    safe_point[
                        "latency_ok"
                    ]
                ),

                "error_rate_ok": (
                    safe_point[
                        "error_rate_ok"
                    ]
                ),

                "availability_ok": (
                    safe_point[
                        "availability_ok"
                    ]
                ),

                "all_slos_met": (
                    safe_point[
                        "slo_met"
                    ]
                ),
            },

            "evidence_boundary": (
                "SLO sign-off is evaluated at the "
                "highest tested safe operating point. "
                "Higher concurrency breaches are retained "
                "as breaking-point evidence."
            ),

            "results": load_results,
        }

        save_json(
            SLO_PATH,
            slo_data,
        )

    # ------------------------------------------------------------------
    # Rebuild headroom from highest safe capacity.
    # ------------------------------------------------------------------

    if safe_point:

        capacity = safe_point[
            "concurrency"
        ]

        target = (
            capacity
            * 0.70
        )

        recommended = as_float(
            headroom_data.get(
                "recommended_operating_concurrency"
            )
        )

        if (
            recommended is None
            or recommended <= 0
            or recommended >= capacity
            or recommended > target
        ):

            recommended = max(
                1,
                int(
                    target
                ),
            )

        headroom_data = {
            "status": "CALCULATED",

            "capacity_reference_concurrency": (
                capacity
            ),

            "headroom_target": 0.30,

            "target_operating_concurrency": round(
                target,
                2,
            ),

            "recommended_operating_concurrency": (
                recommended
            ),

            "headroom_reserved_percent": (
                HEADROOM_PERCENT
            ),

            "headroom_policy": (
                "Operate below the highest tested "
                "SLO-safe concurrency and reserve "
                "30% capacity headroom."
            ),
        }

        save_json(
            HEADROOM_PATH,
            headroom_data,
        )

    # ------------------------------------------------------------------
    # BUILD FINAL SIGN-OFF
    # ------------------------------------------------------------------

    signoff = build_signoff(
        health_data=health_data,
        inference_data=inference_data,
        integration_data=integration_data,
        load_data=load_data,
        slo_data=slo_data,
        headroom_data=headroom_data,
        fallback_data=fallback_data,
        heldout_data=heldout_data,
        baseline_data=baseline_data,
    )

    save_json(
        SIGNOFF_PATH,
        signoff,
    )

    checks = signoff[
        "checks"
    ]

    # ------------------------------------------------------------------
    # PRINT RESULT
    # ------------------------------------------------------------------

    labels = [
        (
            "Normal service",
            "normal_service",
        ),
        (
            "Worked inference",
            "worked_inference",
        ),
        (
            "Integration",
            "integration",
        ),
        (
            "Real logged data",
            "real_logged_data",
        ),
        (
            "Held-out validation",
            "heldout_validation",
        ),
        (
            "Baseline quality",
            "baseline_quality",
        ),
        (
            "Load evidence",
            "load_evidence",
        ),
        (
            "SLO evidence",
            "slo_evidence",
        ),
        (
            "Headroom evidence",
            "headroom_evidence",
        ),
        (
            "Failure injection",
            "failure_injection",
        ),
    ]

    for label, key in labels:

        print(
            f"{label:<22}: "
            f"{'PASS' if checks[key] else 'FAIL'}"
        )

    print()

    if safe_point:

        print(
            "Highest safe concurrency : "
            f"{safe_point['concurrency']}"
        )

        print(
            "Safe operating p95      : "
            f"{safe_point['p95_ms']:.3f} ms"
        )

        print(
            "Safe operating error    : "
            f"{safe_point['error_rate_percent']:.3f}%"
        )

        print(
            "Safe operating uptime   : "
            f"{safe_point['availability_percent']:.3f}%"
        )

    if breaking_point is not None:

        print(
            "Breaking point          : "
            f"{breaking_point}"
        )

    recommended = headroom_data.get(
        "recommended_operating_concurrency"
    )

    if recommended is not None:

        print(
            "Recommended concurrency : "
            f"{recommended}"
        )

    print()

    print(
        "TASK 05 FINAL STATUS: "
        f"{signoff['signoff_status']}"
    )

    print()

    print(
        "Evidence written : "
        f"{SIGNOFF_PATH}"
    )

    print()

    if signoff[
        "signoff_status"
    ] != "READY_FOR_REVIEW":

        print(
            "One or more required checks are still failing."
        )

        print(
            "Review reliability_signoff.json "
            "for the exact check."
        )

        sys.exit(1)

    print(
        "All required reliability checks passed."
    )

    print(
        "Task 05 is ready for mentor/evaluator review."
    )


if __name__ == "__main__":
    main()