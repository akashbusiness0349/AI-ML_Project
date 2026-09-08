import json
from pathlib import Path
from statistics import mean


MODEL_VERSION = "v1-drift-monitor"
RETRAINED_MODEL_VERSION = "v2-drift-retrained"

DRIFT_THRESHOLD = 0.20
PRECISION_DROP_THRESHOLD = 0.05
RECALL_DROP_THRESHOLD = 0.05


def load_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_quality(records):
    tp = sum(
        1 for r in records
        if r["recommended"] and r["relevant"]
    )

    fp = sum(
        1 for r in records
        if r["recommended"] and not r["relevant"]
    )

    fn = sum(
        1 for r in records
        if not r["recommended"] and r["relevant"]
    )

    tn = sum(
        1 for r in records
        if not r["recommended"] and not r["relevant"]
    )

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "records": len(records),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4)
    }


def score_bins(records):
    bins = {
        "0.0-0.2": 0,
        "0.2-0.4": 0,
        "0.4-0.6": 0,
        "0.6-0.8": 0,
        "0.8-1.0": 0
    }

    for record in records:
        score = record["score"]

        if score < 0.2:
            bins["0.0-0.2"] += 1
        elif score < 0.4:
            bins["0.2-0.4"] += 1
        elif score < 0.6:
            bins["0.4-0.6"] += 1
        elif score < 0.8:
            bins["0.6-0.8"] += 1
        else:
            bins["0.8-1.0"] += 1

    return bins


def calculate_psi(reference, current):
    """
    Population Stability Index.

    PSI interpretation:
    < 0.10  = little/no drift
    0.10-0.20 = moderate drift
    >= 0.20 = significant drift
    """

    reference_bins = score_bins(reference)
    current_bins = score_bins(current)

    total_reference = len(reference)
    total_current = len(current)

    psi = 0.0
    details = {}

    for bucket in reference_bins:
        ref_pct = reference_bins[bucket] / total_reference
        cur_pct = current_bins[bucket] / total_current

        # Small smoothing value prevents log(0).
        ref_pct_safe = max(ref_pct, 0.0001)
        cur_pct_safe = max(cur_pct, 0.0001)

        contribution = (
            (cur_pct_safe - ref_pct_safe)
            * __import__("math").log(
                cur_pct_safe / ref_pct_safe
            )
        )

        psi += contribution

        details[bucket] = {
            "reference_count": reference_bins[bucket],
            "current_count": current_bins[bucket],
            "reference_pct": round(ref_pct, 4),
            "current_pct": round(cur_pct, 4),
            "psi_contribution": round(contribution, 4)
        }

    return {
        "psi": round(psi, 4),
        "buckets": details
    }


def calculate_mean_shift(reference, current):
    reference_mean = mean(r["score"] for r in reference)
    current_mean = mean(r["score"] for r in current)

    return {
        "reference_mean": round(reference_mean, 4),
        "current_mean": round(current_mean, 4),
        "absolute_shift": round(
            abs(current_mean - reference_mean),
            4
        )
    }


def build_report(reference, current):
    reference_quality = calculate_quality(reference)
    current_quality = calculate_quality(current)

    psi_result = calculate_psi(reference, current)
    mean_shift = calculate_mean_shift(reference, current)

    precision_drop = (
        reference_quality["precision"]
        - current_quality["precision"]
    )

    recall_drop = (
        reference_quality["recall"]
        - current_quality["recall"]
    )

    drift_detected = psi_result["psi"] >= DRIFT_THRESHOLD

    quality_regression = (
        precision_drop >= PRECISION_DROP_THRESHOLD
        or recall_drop >= RECALL_DROP_THRESHOLD
    )

    retraining_required = drift_detected or quality_regression

    return {
        "model_version": MODEL_VERSION,
        "reference_records": len(reference),
        "current_records": len(current),

        "reference_quality": reference_quality,
        "current_quality": current_quality,

        "drift": {
            "psi": psi_result["psi"],
            "threshold": DRIFT_THRESHOLD,
            "detected": drift_detected,
            "mean_shift": mean_shift,
            "distribution": psi_result["buckets"]
        },

        "quality_regression": {
            "precision_drop": round(precision_drop, 4),
            "recall_drop": round(recall_drop, 4),
            "precision_threshold": PRECISION_DROP_THRESHOLD,
            "recall_threshold": RECALL_DROP_THRESHOLD,
            "detected": quality_regression
        },

        "retraining": {
            "required": retraining_required,
            "performed": False,
            "new_model_version": None,
            "reason": []
        },

        "pipeline_status": "MONITORING"
    }


def retrain_model(report):
    """
    Deterministic model refresh/recalibration step.

    This intentionally represents the retraining stage without
    pretending that a production ML training job or model registry
    exists yet.
    """

    if not report["retraining"]["required"]:
        return report

    reasons = []

    if report["drift"]["detected"]:
        reasons.append("SIGNIFICANT_DRIFT")

    if report["quality_regression"]["detected"]:
        reasons.append("QUALITY_REGRESSION")

    report["retraining"]["performed"] = True
    report["retraining"]["new_model_version"] = RETRAINED_MODEL_VERSION
    report["retraining"]["reason"] = reasons

    report["pipeline_status"] = "RETRAINED"

    return report


def save_report(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def load_report(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)