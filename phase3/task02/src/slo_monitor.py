
import hashlib
import json
import math
import statistics
from pathlib import Path


MODEL_VERSION = "v1-mlops-baseline"

# Engineering SLO targets for the PlaceMux intelligence layer.
P95_LATENCY_SLO_MS = 100.0
AVAILABILITY_SLO = 0.99
MIN_PRECISION_SLO = 0.80

# Existing project monitoring threshold.
PSI_THRESHOLD = 0.20

# Score-distribution safety checks.
SCORE_MIN = 0.0
SCORE_MAX = 1.0
DEGENERATE_UNIQUE_SCORE_LIMIT = 1


def load_json(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def sha256_file(path):
    path = Path(path)
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def calculate_confusion_matrix(events):
    valid_events = [
        event for event in events
        if not event.get("error", False)
    ]

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for event in valid_events:
        predicted = bool(event["recommended"])
        actual = bool(event["relevant"])

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1

    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
    }


def calculate_quality(events):
    matrix = calculate_confusion_matrix(events)

    tp = matrix["true_positive"]
    fp = matrix["false_positive"]
    tn = matrix["true_negative"]
    fn = matrix["false_negative"]

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    fpr = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    return {
        **matrix,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "false_positive_rate": round(fpr, 4),
    }


def calculate_latency(events):
    latencies = [
        float(event["latency_ms"])
        for event in events
        if not event.get("error", False)
    ]

    if not latencies:
        return {
            "count": 0,
            "average_ms": 0.0,
            "p95_ms": 0.0,
            "maximum_ms": 0.0,
        }

    sorted_latencies = sorted(latencies)

    # Nearest-rank style p95, with a minimum index of 1.
    rank = max(
        1,
        math.ceil(0.95 * len(sorted_latencies))
    )

    p95 = sorted_latencies[rank - 1]

    return {
        "count": len(latencies),
        "average_ms": round(
            statistics.mean(latencies), 2
        ),
        "p95_ms": round(p95, 2),
        "maximum_ms": round(max(latencies), 2),
    }


def calculate_availability(events):
    total = len(events)

    if total == 0:
        return {
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "availability": 0.0,
        }

    failed = sum(
        1
        for event in events
        if event.get("error", False)
    )

    successful = total - failed

    return {
        "total_events": total,
        "successful_events": successful,
        "failed_events": failed,
        "availability": round(
            successful / total,
            4
        ),
    }


def calculate_score_distribution(events):
    scores = [
        float(event["match_score"])
        for event in events
        if not event.get("error", False)
    ]

    if not scores:
        return {
            "count": 0,
            "mean": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
            "unique_values": 0,
            "degenerate": True,
        }

    unique_values = len(set(scores))

    return {
        "count": len(scores),
        "mean": round(statistics.mean(scores), 4),
        "minimum": round(min(scores), 4),
        "maximum": round(max(scores), 4),
        "unique_values": unique_values,
        "degenerate": (
            unique_values <= DEGENERATE_UNIQUE_SCORE_LIMIT
        ),
    }


def calculate_psi(reference_scores, current_scores):
    bins = [0.0, 0.25, 0.50, 0.75, 1.01]

    def distribution(scores):
        counts = [0] * (len(bins) - 1)

        for score in scores:
            for index in range(len(bins) - 1):
                if bins[index] <= score < bins[index + 1]:
                    counts[index] += 1
                    break

        total = len(scores)

        if total == 0:
            return [0.0] * len(counts)

        return [
            count / total
            for count in counts
        ]

    reference = distribution(reference_scores)
    current = distribution(current_scores)

    psi = 0.0

    for ref, cur in zip(reference, current):
        ref = max(ref, 0.0001)
        cur = max(cur, 0.0001)

        psi += (
            (cur - ref)
            * math.log(cur / ref)
        )

    return round(psi, 4)


def build_slo_report(
    events,
    reference_scores,
    source_path,
    offline_reference=None,
):
    quality = calculate_quality(events)
    latency = calculate_latency(events)
    availability = calculate_availability(events)
    score_distribution = calculate_score_distribution(events)

    current_scores = [
        float(event["match_score"])
        for event in events
        if not event.get("error", False)
    ]

    psi = calculate_psi(
        reference_scores,
        current_scores
    )

    precision_slo_pass = (
        quality["precision"] >= MIN_PRECISION_SLO
    )

    latency_slo_pass = (
        latency["p95_ms"] <= P95_LATENCY_SLO_MS
    )

    availability_slo_pass = (
        availability["availability"] >= AVAILABILITY_SLO
    )

    score_distribution_pass = (
        not score_distribution["degenerate"]
    )

    psi_pass = psi <= PSI_THRESHOLD

    return {
        "task": "Phase 3 Task 02",
        "model_version": MODEL_VERSION,
        "scope": "production-style-go-live-rehearsal",
        "external_production": False,
        "data_provenance": {
            "source_file": str(Path(source_path).resolve()),
            "source_sha256": sha256_file(source_path),
            "event_count": len(events),
        },
        "slo_targets": {
            "p95_latency_ms": P95_LATENCY_SLO_MS,
            "availability": AVAILABILITY_SLO,
            "minimum_precision": MIN_PRECISION_SLO,
            "psi_threshold": PSI_THRESHOLD,
        },
        "observed": {
            "quality": quality,
            "latency": latency,
            "availability": availability,
            "score_distribution": score_distribution,
            "psi": psi,
        },
        "slo_results": {
            "p95_latency": {
                "target": P95_LATENCY_SLO_MS,
                "actual": latency["p95_ms"],
                "pass": latency_slo_pass,
            },
            "availability": {
                "target": AVAILABILITY_SLO,
                "actual": availability["availability"],
                "pass": availability_slo_pass,
            },
            "minimum_precision": {
                "target": MIN_PRECISION_SLO,
                "actual": quality["precision"],
                "pass": precision_slo_pass,
            },
            "score_distribution": {
                "unique_values": score_distribution["unique_values"],
                "degenerate": score_distribution["degenerate"],
                "pass": score_distribution_pass,
            },
            "prediction_drift": {
                "psi": psi,
                "threshold": PSI_THRESHOLD,
                "pass": psi_pass,
            },
        },
        "offline_reference": offline_reference,
        "explainability": {
            "method": "match_score_threshold",
            "threshold": 0.70,
            "example": {
                "input": {
                    "candidate_id": "student_001",
                    "job_id": "job_001",
                },
                "output": {
                    "match_score": 1.0,
                    "recommended": True,
                },
                "plain_english_reason":
                    "The match score is at or above the recommendation threshold, so the candidate is recommended.",
            },
        },
        "model_unavailable_behavior": {
            "status": "MODEL_UNAVAILABLE",
            "fallback": "return_no_recommendation",
            "safe": True,
        },
    }
