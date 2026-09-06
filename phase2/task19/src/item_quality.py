import json
from pathlib import Path


MODEL_VERSION = "v1-item-quality"


def load_items(path):
    """Load item-bank records from JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_accuracy(correct, attempts):
    """Calculate overall item accuracy."""
    if attempts == 0:
        return 0.0

    return correct / attempts


def calculate_discrimination(high_correct, high_attempts, low_correct, low_attempts):
    """Calculate simple high-vs-low performer discrimination."""
    high_rate = calculate_accuracy(high_correct, high_attempts)
    low_rate = calculate_accuracy(low_correct, low_attempts)

    return high_rate - low_rate


def analyze_item(item):
    """Analyze one assessment item and determine whether it needs review."""

    attempts = item["attempts"]
    correct = item["correct"]

    accuracy = calculate_accuracy(correct, attempts)

    discrimination = calculate_discrimination(
        item["high_performer_correct"],
        item["high_performer_attempts"],
        item["low_performer_correct"],
        item["low_performer_attempts"],
    )

    reasons = []

    # Weak-item rules
    if attempts < 20:
        reasons.append("Low attempt count")

    if accuracy < 0.40:
        reasons.append("Very low overall accuracy")

    if accuracy > 0.90:
        reasons.append("Very high overall accuracy")

    if discrimination < 0.10:
        reasons.append(
            "Low discrimination between stronger and weaker performers"
        )

    if item.get("ambiguous", False):
        reasons.append("Item marked as potentially ambiguous")

    weak_item = len(reasons) > 0

    return {
        "item_id": item["item_id"],
        "college_id": item["college_id"],
        "question": item["question"],
        "attempts": attempts,
        "accuracy": round(accuracy, 4),
        "discrimination": round(discrimination, 4),
        "weak_item": weak_item,
        "status": "REVIEW" if weak_item else "KEEP",
        "reasons": reasons,
    }


def analyze_item_bank(items):
    """Analyze the complete item bank."""

    results = [
        analyze_item(item)
        for item in items
    ]

    weak_items = [
        item for item in results
        if item["weak_item"]
    ]

    keep_items = [
        item for item in results
        if not item["weak_item"]
    ]

    total_items = len(results)

    weak_item_rate = (
        len(weak_items) / total_items
        if total_items > 0
        else 0.0
    )

    return {
        "model_version": MODEL_VERSION,
        "total_items": total_items,
        "weak_item_count": len(weak_items),
        "weak_item_rate": round(weak_item_rate, 4),
        "keep_item_count": len(keep_items),
        "items": results,
    }


def filter_items_by_college(report, college_id):
    """Return only items belonging to the requested college."""

    return [
        item
        for item in report["items"]
        if item["college_id"] == college_id
    ]


def validate_college_isolation(report):
    """
    Validate that item records retain their college ownership.

    Production systems should additionally enforce tenant isolation
    through authenticated API/database authorization.
    """

    college_ids = {
        item["college_id"]
        for item in report["items"]
    }

    isolation_pass = all(
        bool(item["college_id"])
        for item in report["items"]
    )

    return {
        "college_count": len(college_ids),
        "college_ids": sorted(college_ids),
        "college_isolation_supported": isolation_pass,
        "decision": "PASS" if isolation_pass else "FAIL",
    }


def save_report(report, path):
    """Persist the item-quality report."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2
        )