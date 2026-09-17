from __future__ import annotations

import csv
import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]

TASK01_LOG = REPO_ROOT / "phase3" / "task01" / "data" / "live_interaction_logs.json"
TASK04_REQUESTS = REPO_ROOT / "phase3" / "task04" / "data" / "inference_requests.json"

DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

INFERENCE_REQUESTS_PATH = DATA_DIR / "inference_requests.json"
HELDOUT_PATH = DATA_DIR / "heldout_validation.json"
INTEGRATION_PATH = LOG_DIR / "integration_results.json"
BASELINE_PATH = LOG_DIR / "baseline_comparison.json"
EXPERIMENT_PATH = LOG_DIR / "experiment_log.csv"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phase3.task05.src.model import SkillMatchingModel


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return float(ordered[0])

    position = (p / 100.0) * (len(ordered) - 1)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return float(ordered[lower])

    fraction = position - lower

    return float(
        ordered[lower]
        + (ordered[upper] - ordered[lower]) * fraction
    )


def normalize(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, str):
        value = value.split(",")

    if not isinstance(value, list):
        return []

    return sorted(
        {
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        }
    )


def extract_skills(
    record: Dict[str, Any],
    keys: List[str],
) -> List[str]:
    for key in keys:
        if key not in record:
            continue

        result = normalize(record[key])

        if result:
            return result

    return []


def convert_record(
    record: Any,
    index: int,
) -> Optional[Dict[str, Any]]:
    if not isinstance(record, dict):
        return None

    candidate_skills = extract_skills(
        record,
        [
            "candidate_skills",
            "candidateSkills",
            "skills",
            "user_skills",
            "userSkills",
        ],
    )

    required_skills = extract_skills(
        record,
        [
            "required_skills",
            "requiredSkills",
            "job_skills",
            "jobSkills",
            "skills_required",
        ],
    )

    payload = record.get("payload")

    if isinstance(payload, dict):
        if not candidate_skills:
            candidate_skills = extract_skills(
                payload,
                [
                    "candidate_skills",
                    "candidateSkills",
                    "skills",
                ],
            )

        if not required_skills:
            required_skills = extract_skills(
                payload,
                [
                    "required_skills",
                    "requiredSkills",
                    "job_skills",
                ],
            )

    if not candidate_skills or not required_skills:
        return None

    request_id = record.get(
        "request_id",
        record.get(
            "id",
            f"task05_request_{index:03d}",
        ),
    )

    return {
        "request_id": str(request_id),
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
    }


def load_task01_data() -> Dict[str, Any]:
    data = load_json(
        TASK01_LOG,
        {},
    )

    if not isinstance(data, dict):
        data = {}

    events = data.get(
        "events",
        [],
    )

    if not isinstance(events, list):
        events = []

    return {
        "events": events,
        "source": str(TASK01_LOG),
        "source_type": data.get(
            "source_type",
            "unknown",
        ),
        "environment": data.get(
            "environment",
            "unknown",
        ),
        "external_production": bool(
            data.get(
                "external_production",
                False,
            )
        ),
        "model_version": data.get(
            "model_version",
            "unknown",
        ),
        "traffic_window": data.get(
            "traffic_window",
            "unknown",
        ),
    }


def analyze_task01_data(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    events = data.get(
        "events",
        [],
    )

    scores: List[float] = []
    latencies: List[float] = []

    recommended_count = 0
    relevant_count = 0
    error_count = 0

    for event in events:
        if not isinstance(event, dict):
            continue

        score = event.get("match_score")

        if isinstance(
            score,
            (int, float),
        ):
            scores.append(
                float(score)
            )

        latency = event.get("latency_ms")

        if isinstance(
            latency,
            (int, float),
        ):
            latencies.append(
                float(latency)
            )

        if event.get("recommended") is True:
            recommended_count += 1

        if event.get("relevant") is True:
            relevant_count += 1

        if event.get("error") is True:
            error_count += 1

    total = len(events)

    return {
        "event_count": total,
        "score_count": len(scores),
        "mean_match_score": round(
            statistics.mean(scores)
            if scores
            else 0.0,
            6,
        ),
        "p95_match_score": round(
            percentile(
                scores,
                95,
            ),
            6,
        ),
        "mean_latency_ms": round(
            statistics.mean(latencies)
            if latencies
            else 0.0,
            6,
        ),
        "p95_latency_ms": round(
            percentile(
                latencies,
                95,
            ),
            6,
        ),
        "recommended_count": recommended_count,
        "relevant_count": relevant_count,
        "error_count": error_count,
        "recommendation_rate_percent": round(
            (
                recommended_count / total * 100.0
                if total
                else 0.0
            ),
            6,
        ),
        "relevance_rate_percent": round(
            (
                relevant_count / total * 100.0
                if total
                else 0.0
            ),
            6,
        ),
        "error_rate_percent": round(
            (
                error_count / total * 100.0
                if total
                else 0.0
            ),
            6,
        ),
    }


def load_task04_requests() -> List[Dict[str, Any]]:
    data = load_json(
        TASK04_REQUESTS,
        {},
    )

    if isinstance(data, dict):
        records = data.get(
            "requests",
            [],
        )
    elif isinstance(data, list):
        records = data
    else:
        records = []

    if not isinstance(records, list):
        return []

    requests: List[Dict[str, Any]] = []

    for index, record in enumerate(
        records,
        start=1,
    ):
        converted = convert_record(
            record,
            index,
        )

        if converted is not None:
            requests.append(
                converted
            )

    return requests


def load_existing_heldout() -> List[Dict[str, Any]]:
    data = load_json(
        HELDOUT_PATH,
        {},
    )

    if isinstance(data, dict):
        records = data.get(
            "records",
            data.get(
                "requests",
                [],
            ),
        )
    elif isinstance(data, list):
        records = data
    else:
        records = []

    if not isinstance(records, list):
        return []

    result: List[Dict[str, Any]] = []

    for index, record in enumerate(
        records,
        start=1,
    ):
        converted = convert_record(
            record,
            index,
        )

        if converted is not None:
            result.append(
                converted
            )

    return result


def prepare_heldout(
    requests: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    existing = load_existing_heldout()

    if len(existing) >= 2:
        return existing

    if len(requests) < 2:
        return []

    count = max(
        2,
        int(len(requests) * 0.2),
    )

    count = min(
        count,
        len(requests),
    )

    return requests[-count:]


def baseline_predict(
    candidate_skills: List[str],
    required_skills: List[str],
) -> Dict[str, Any]:
    candidate = set(
        normalize(candidate_skills)
    )

    required = normalize(
        required_skills
    )

    matched = sorted(
        candidate.intersection(required)
    )

    missing = sorted(
        set(required) - set(matched)
    )

    score = (
        len(matched) / len(required)
        if required
        else 0.0
    )

    decision = (
        "MATCH"
        if score >= 0.7
        else "NO_MATCH"
    )

    return {
        "score": round(
            score,
            6,
        ),
        "decision": decision,
        "matched_skills": matched,
        "missing_skills": missing,
    }


def evaluate_heldout(
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not records:
        return {
            "passed": False,
            "record_count": 0,
            "decision_consistency_percent": 0.0,
            "score_consistency_percent": 0.0,
            "comparisons": [],
        }

    model = SkillMatchingModel()

    decision_matches = 0
    score_matches = 0
    latencies: List[float] = []
    comparisons: List[Dict[str, Any]] = []

    for request in records:
        candidate = request[
            "candidate_skills"
        ]

        required = request[
            "required_skills"
        ]

        baseline = baseline_predict(
            candidate,
            required,
        )

        started = time.perf_counter()

        result = model.predict(
            candidate_skills=candidate,
            required_skills=required,
        )

        latency = (
            time.perf_counter()
            - started
        ) * 1000.0

        latencies.append(
            latency
        )

        decision_same = (
            baseline["decision"]
            == result.decision
        )

        score_same = (
            abs(
                baseline["score"]
                - result.score
            )
            <= 1e-6
        )

        if decision_same:
            decision_matches += 1

        if score_same:
            score_matches += 1

        comparisons.append(
            {
                "request_id": request[
                    "request_id"
                ],
                "baseline_score": baseline[
                    "score"
                ],
                "optimized_score": result.score,
                "baseline_decision": baseline[
                    "decision"
                ],
                "optimized_decision": result.decision,
                "decision_same": decision_same,
                "score_same": score_same,
            }
        )

    total = len(records)

    decision_consistency = (
        decision_matches / total * 100.0
    )

    score_consistency = (
        score_matches / total * 100.0
    )

    return {
        "passed": (
            decision_consistency == 100.0
            and score_consistency == 100.0
        ),
        "record_count": total,
        "decision_consistency_percent": round(
            decision_consistency,
            6,
        ),
        "score_consistency_percent": round(
            score_consistency,
            6,
        ),
        "optimized_p95_latency_ms": round(
            percentile(
                latencies,
                95,
            ),
            6,
        ),
        "comparisons": comparisons,
    }


def write_experiment_log(
    task01_metrics: Dict[str, Any],
    validation: Dict[str, Any],
) -> None:
    rows = [
        {
            "timestamp_utc": utc_now(),
            "metric": "task01_event_count",
            "value": task01_metrics[
                "event_count"
            ],
            "status": (
                "PASS"
                if task01_metrics[
                    "event_count"
                ] > 0
                else "FAIL"
            ),
        },
        {
            "timestamp_utc": utc_now(),
            "metric": "decision_consistency_percent",
            "value": validation[
                "decision_consistency_percent"
            ],
            "status": (
                "PASS"
                if validation[
                    "decision_consistency_percent"
                ] == 100.0
                else "FAIL"
            ),
        },
        {
            "timestamp_utc": utc_now(),
            "metric": "score_consistency_percent",
            "value": validation[
                "score_consistency_percent"
            ],
            "status": (
                "PASS"
                if validation[
                    "score_consistency_percent"
                ] == 100.0
                else "FAIL"
            ),
        },
    ]

    with EXPERIMENT_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp_utc",
                "metric",
                "value",
                "status",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "PHASE 3 / TASK 05 — INTEGRATED RELIABILITY SIGN-OFF"
    )

    task01 = load_task01_data()
    task01_metrics = analyze_task01_data(
        task01
    )

    print(
        f"Task 01 logged events : "
        f"{task01_metrics['event_count']}"
    )

    print(
        f"External production   : "
        f"{task01['external_production']}"
    )

    requests = load_task04_requests()

    print(
        f"Task 04 usable records: "
        f"{len(requests)}"
    )

    heldout = prepare_heldout(
        requests
    )

    save_json(
        HELDOUT_PATH,
        {
            "task": "Phase 3 Task 05",
            "record_count": len(heldout),
            "records": heldout,
        },
    )

    save_json(
        INFERENCE_REQUESTS_PATH,
        {
            "task": "Phase 3 Task 05",
            "source": str(TASK04_REQUESTS),
            "source_type": "sprint_a_control_data",
            "record_count": len(requests),
            "requests": requests,
        },
    )

    validation = evaluate_heldout(
        heldout
    )

    save_json(
        BASELINE_PATH,
        {
            "generated_at_utc": utc_now(),
            "task": "Phase 3 Task 05",
            "comparison": "baseline_vs_optimized_model",
            "quality_preserved": validation[
                "passed"
            ],
            "heldout_evaluation": validation,
        },
    )

    integration_passed = (
        task01_metrics[
            "event_count"
        ] > 0
        and len(requests) > 0
        and len(heldout) >= 2
        and validation["passed"]
    )

    integration = {
        "generated_at_utc": utc_now(),
        "task": "Phase 3 Task 05",
        "status": (
            "PASS"
            if integration_passed
            else "FAIL"
        ),
        "good_definition": (
            "Matching stays correct, fast and "
            "observable under sustained realistic load."
        ),
        "real_logged_data_available": (
            task01_metrics[
                "event_count"
            ] > 0
        ),
        "logged_data_sources": {
            "task01": {
                "path": str(TASK01_LOG),
                "records": task01_metrics[
                    "event_count"
                ],
                "source_type": task01[
                    "source_type"
                ],
                "environment": task01[
                    "environment"
                ],
                "external_production": task01[
                    "external_production"
                ],
            },
            "task04": {
                "path": str(TASK04_REQUESTS),
                "records": len(requests),
            },
        },
        "task01_observed_metrics": task01_metrics,
        "heldout_validation": validation,
        "baseline_comparison": str(
            BASELINE_PATH
        ),
        "experiment_log": str(
            EXPERIMENT_PATH
        ),
        "integrated_evidence": {
            "task02": "phase3/task02/logs",
            "task03": "phase3/task03/logs",
            "task04": "phase3/task04/logs",
        },
    }

    save_json(
        INTEGRATION_PATH,
        integration,
    )

    write_experiment_log(
        task01_metrics,
        validation,
    )

    print(
        f"Held-out records      : "
        f"{len(heldout)}"
    )

    print(
        f"Decision consistency  : "
        f"{validation['decision_consistency_percent']:.2f}%"
    )

    print(
        f"Score consistency     : "
        f"{validation['score_consistency_percent']:.2f}%"
    )

    print(
        f"Integration status    : "
        f"{'PASS' if integration_passed else 'FAIL'}"
    )


if __name__ == "__main__":
    main()