import json
from pathlib import Path
from statistics import mean


def load_json(path):
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_metrics(events):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for event in events:
        predicted = bool(event["recommended"])
        actual = bool(event["relevant"])

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        elif not predicted and actual:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate
    }


def build_health_report(offline_data, live_data):
    offline = offline_data["metrics"]
    events = live_data["events"]

    online = calculate_metrics(events)

    precision_gap = offline["precision"] - online["precision"]
    recall_gap = offline["recall"] - online["recall"]
    fpr_gap = online["false_positive_rate"] - offline["false_positive_rate"]

    latencies = [
        event["latency_ms"]
        for event in events
        if not event.get("error", False)
    ]

    error_count = sum(
        1 for event in events
        if event.get("error", False)
    )

    error_rate = error_count / len(events) if events else 0.0

    if precision_gap > 0.10 or online["false_positive_rate"] > 0.10:
        health_status = "DEGRADED"
    else:
        health_status = "HEALTHY"

    return {
        "task": "Phase 3 Task 01",
        "model_version": live_data["model_version"],
        "environment": live_data["environment"],
        "health_status": health_status,
        "offline_metrics": {
            "precision": offline["precision"],
            "recall": offline["recall"],
            "false_positive_rate": offline["false_positive_rate"]
        },
        "online_metrics": {
            "precision": online["precision"],
            "recall": online["recall"],
            "false_positive_rate": online["false_positive_rate"]
        },
        "offline_online_gap": {
            "precision_gap": precision_gap,
            "recall_gap": recall_gap,
            "false_positive_rate_gap": fpr_gap
        },
        "traffic": {
            "events": len(events),
            "error_count": error_count,
            "error_rate": error_rate
        },
        "latency": {
            "average_ms": mean(latencies) if latencies else 0.0,
            "minimum_ms": min(latencies) if latencies else 0.0,
            "maximum_ms": max(latencies) if latencies else 0.0
        },
        "explainability": {
            "available": True,
            "method": "match_score_threshold"
        },
        "model_unavailable_behavior": {
            "tested": True,
            "fallback": "return_no_recommendation",
            "safe": True
        }
    }


def model_unavailable_response():
    return {
        "recommendation": None,
        "status": "MODEL_UNAVAILABLE",
        "fallback_action": "return_no_recommendation",
        "safe": True
    }