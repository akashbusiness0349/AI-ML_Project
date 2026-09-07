from pathlib import Path
import json


MODEL_VERSION = "v1-fairness-audit"


def load_data(path):
    """Load fairness audit records from JSON."""

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_rate(numerator, denominator):
    """Calculate a rate safely."""

    if denominator == 0:
        return 0.0

    return numerator / denominator


def calculate_group_metrics(records):
    """Calculate recommendation metrics for each group."""

    groups = sorted(
        {
            record["group"]
            for record in records
        }
    )

    metrics = {}

    for group in groups:
        group_records = [
            record
            for record in records
            if record["group"] == group
        ]

        total = len(group_records)

        recommended = sum(
            1
            for record in group_records
            if record["recommended"]
        )

        relevant = sum(
            1
            for record in group_records
            if record["relevant"]
        )

        true_positive = sum(
            1
            for record in group_records
            if record["recommended"]
            and record["relevant"]
        )

        false_positive = sum(
            1
            for record in group_records
            if record["recommended"]
            and not record["relevant"]
        )

        actual_negative = sum(
            1
            for record in group_records
            if not record["relevant"]
        )

        actual_positive = sum(
            1
            for record in group_records
            if record["relevant"]
        )

        selection_rate = calculate_rate(
            recommended,
            total
        )

        true_positive_rate = calculate_rate(
            true_positive,
            actual_positive
        )

        false_positive_rate = calculate_rate(
            false_positive,
            actual_negative
        )

        precision = calculate_rate(
            true_positive,
            recommended
        )

        metrics[group] = {
            "total_records": total,
            "recommended": recommended,
            "relevant": relevant,
            "true_positive": true_positive,
            "false_positive": false_positive,
            "selection_rate": round(selection_rate, 4),
            "true_positive_rate": round(true_positive_rate, 4),
            "false_positive_rate": round(false_positive_rate, 4),
            "precision": round(precision, 4),
        }

    return metrics


def calculate_disparity(metrics, metric_name):
    """Calculate maximum absolute group disparity."""

    values = [
        metrics[group][metric_name]
        for group in metrics
    ]

    if not values:
        return 0.0

    return max(values) - min(values)


def calculate_disparate_impact(metrics):
    """
    Calculate the minimum-to-maximum selection-rate ratio.

    A value closer to 1 means the group selection rates
    are closer to each other.
    """

    selection_rates = [
        metrics[group]["selection_rate"]
        for group in metrics
    ]

    if not selection_rates:
        return 0.0

    maximum = max(selection_rates)
    minimum = min(selection_rates)

    if maximum == 0:
        return 1.0

    return minimum / maximum


def build_fairness_report(records):
    """Build the complete fairness audit report."""

    group_metrics = calculate_group_metrics(records)

    selection_rate_disparity = calculate_disparity(
        group_metrics,
        "selection_rate"
    )

    tpr_disparity = calculate_disparity(
        group_metrics,
        "true_positive_rate"
    )

    fpr_disparity = calculate_disparity(
        group_metrics,
        "false_positive_rate"
    )

    precision_disparity = calculate_disparity(
        group_metrics,
        "precision"
    )

    disparate_impact = calculate_disparate_impact(
        group_metrics
    )

    return {
        "model_version": MODEL_VERSION,
        "audit_status": "UNDERWAY",
        "total_records": len(records),
        "group_count": len(group_metrics),
        "group_metrics": group_metrics,
        "fairness_metrics": {
            "selection_rate_disparity": round(
                selection_rate_disparity,
                4
            ),
            "true_positive_rate_disparity": round(
                tpr_disparity,
                4
            ),
            "false_positive_rate_disparity": round(
                fpr_disparity,
                4
            ),
            "precision_disparity": round(
                precision_disparity,
                4
            ),
            "disparate_impact_ratio": round(
                disparate_impact,
                4
            ),
        },
        "notes": [
            "This is an initial fairness audit.",
            "Group labels are synthetic or real-shaped audit segments.",
            "Metrics identify disparities but do not by themselves prove discrimination.",
            "Further review is required before production launch."
        ],
    }


def validate_group_coverage(report):
    """Verify that every group contains audit records."""

    metrics = report["group_metrics"]

    if not metrics:
        return False

    return all(
        values["total_records"] > 0
        for values in metrics.values()
    )


def filter_by_group(report, group):
    """Return audit metrics for one group."""

    return report["group_metrics"].get(
        group,
        {}
    )


def save_report(report, path):
    """Persist fairness audit report."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=2
        )


if __name__ == "__main__":
    print("Fairness audit module loaded.")