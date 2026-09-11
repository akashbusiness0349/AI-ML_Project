import json
import statistics
from pathlib import Path


MODEL_VERSION = "v1-mlops-baseline"
RECOMMENDATION_THRESHOLD = 0.70
LATENCY_THRESHOLD_MS = 100.0
ERROR_RATE_THRESHOLD = 0.05
PSI_THRESHOLD = 0.20


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def calculate_quality(events):
    valid_events = [event for event in events if not event["error"]]

    if not valid_events:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "fpr": 0.0
        }

    recommended = sum(
        event["recommended"]
        for event in valid_events
    )

    relevant = sum(
        event["relevant"]
        for event in valid_events
    )

    true_positive = sum(
        event["recommended"] and event["relevant"]
        for event in valid_events
    )

    false_positive = sum(
        event["recommended"] and not event["relevant"]
        for event in valid_events
    )

    non_relevant = len(valid_events) - relevant

    precision = (
        true_positive / recommended
        if recommended else 0.0
    )

    recall = (
        true_positive / relevant
        if relevant else 0.0
    )

    fpr = (
        false_positive / non_relevant
        if non_relevant else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4)
    }


def calculate_latency(events):
    latencies = [
        event["latency_ms"]
        for event in events
        if not event["error"]
    ]

    if not latencies:
        return {
            "average_ms": 0.0,
            "p95_ms": 0.0,
            "max_ms": 0.0
        }

    sorted_latencies = sorted(latencies)

    p95_index = max(
        0,
        int(len(sorted_latencies) * 0.95) - 1
    )

    return {
        "average_ms": round(
            statistics.mean(latencies), 2
        ),
        "p95_ms": round(
            sorted_latencies[p95_index], 2
        ),
        "max_ms": round(
            max(latencies), 2
        )
    }


def calculate_prediction_distribution(events):
    scores = [
        event["match_score"]
        for event in events
        if not event["error"]
    ]

    if not scores:
        return {
            "count": 0,
            "mean": 0.0,
            "min": 0.0,
            "max": 0.0
        }

    return {
        "count": len(scores),
        "mean": round(statistics.mean(scores), 4),
        "min": round(min(scores), 4),
        "max": round(max(scores), 4)
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

        psi += (cur - ref) * (
            __import__("math").log(cur / ref)
        )

    return round(psi, 4)


def calculate_error_rate(events):
    if not events:
        return 0.0

    errors = sum(
        event["error"]
        for event in events
    )

    return round(errors / len(events), 4)


def check_model_version(events):
    return all(
        event.get("model_version", MODEL_VERSION)
        == MODEL_VERSION
        for event in events
    )


def run_monitoring(events, reference_scores):
    valid_events = [
        event for event in events
        if not event["error"]
    ]

    quality = calculate_quality(events)
    latency = calculate_latency(events)
    prediction_distribution = calculate_prediction_distribution(
        events
    )

    error_rate = calculate_error_rate(events)

    current_scores = [
        event["match_score"]
        for event in valid_events
    ]

    psi = calculate_psi(
        reference_scores,
        current_scores
    )

    alerts = []

    if latency["p95_ms"] > LATENCY_THRESHOLD_MS:
        alerts.append("LATENCY_BREACH")

    if error_rate > ERROR_RATE_THRESHOLD:
        alerts.append("ERROR_RATE_BREACH")

    if psi > PSI_THRESHOLD:
        alerts.append("PREDICTION_DRIFT")

    if quality["precision"] < 0.80:
        alerts.append("PRECISION_REGRESSION")

    if quality["recall"] < 0.80:
        alerts.append("RECALL_REGRESSION")

    model_version_ok = check_model_version(events)

    if not model_version_ok:
        alerts.append("MODEL_VERSION_MISMATCH")

    if alerts:
        health_status = "DEGRADED"
    else:
        health_status = "HEALTHY"

    return {
        "model_version": MODEL_VERSION,
        "environment": "production",
        "traffic_events": len(events),
        "successful_events": len(valid_events),
        "error_rate": error_rate,
        "quality": quality,
        "latency": latency,
        "prediction_distribution": prediction_distribution,
        "psi": psi,
        "psi_threshold": PSI_THRESHOLD,
        "model_version_valid": model_version_ok,
        "alerts": alerts,
        "health_status": health_status,
        "monitoring_status": "LIVE"
    }


def validate_monitoring_report(report):
    required_fields = [
        "model_version",
        "environment",
        "traffic_events",
        "successful_events",
        "error_rate",
        "quality",
        "latency",
        "prediction_distribution",
        "psi",
        "alerts",
        "health_status",
        "monitoring_status"
    ]

    return all(
        field in report
        for field in required_fields
    )


def explain_prediction(event):
    score = event["match_score"]

    if score >= RECOMMENDATION_THRESHOLD:
        reason = (
            "The candidate-job match score is at or above "
            "the recommendation threshold."
        )
    else:
        reason = (
            "The candidate-job match score is below "
            "the recommendation threshold."
        )

    return {
        "event_id": event["event_id"],
        "match_score": score,
        "recommendation": event["recommended"],
        "plain_english_reason": reason
    }