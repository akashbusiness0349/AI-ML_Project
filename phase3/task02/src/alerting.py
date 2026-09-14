
from .slo_monitor import (
    MIN_PRECISION_SLO,
    P95_LATENCY_SLO_MS,
    PSI_THRESHOLD,
)


def evaluate_alerts(slo_report):
    alerts = []

    latency = slo_report["observed"]["latency"]
    quality = slo_report["observed"]["quality"]
    availability = slo_report["observed"]["availability"]
    score_distribution = slo_report["observed"]["score_distribution"]
    psi = slo_report["observed"]["psi"]

    if latency["p95_ms"] > P95_LATENCY_SLO_MS:
        alerts.append({
            "alert": "LATENCY_SLO_BREACH",
            "severity": "HIGH",
            "actual": latency["p95_ms"],
            "threshold": P95_LATENCY_SLO_MS,
            "message": "P95 inference latency exceeded the SLO.",
            "owner": "DevOps",
        })

    if availability["availability"] < 0.99:
        alerts.append({
            "alert": "AVAILABILITY_SLO_BREACH",
            "severity": "CRITICAL",
            "actual": availability["availability"],
            "threshold": 0.99,
            "message": "Model service availability fell below the SLO.",
            "owner": "DevOps",
        })

    if quality["precision"] < MIN_PRECISION_SLO:
        alerts.append({
            "alert": "PRECISION_SLO_BREACH",
            "severity": "HIGH",
            "actual": quality["precision"],
            "threshold": MIN_PRECISION_SLO,
            "message": "Online recommendation precision fell below the quality floor.",
            "owner": "ML Engineer",
        })

    if score_distribution["degenerate"]:
        alerts.append({
            "alert": "DEGENERATE_SCORE_DISTRIBUTION",
            "severity": "HIGH",
            "actual": score_distribution["unique_values"],
            "threshold": 1,
            "message": "Model scores collapsed to a constant value.",
            "owner": "ML Engineer",
        })

    if psi > PSI_THRESHOLD:
        alerts.append({
            "alert": "PREDICTION_DRIFT",
            "severity": "MEDIUM",
            "actual": psi,
            "threshold": PSI_THRESHOLD,
            "message": "Prediction-score distribution drift exceeded the monitoring threshold.",
            "owner": "ML Engineer",
        })

    return alerts


def build_alert_report(slo_report, run_name):
    alerts = evaluate_alerts(slo_report)

    return {
        "task": "Phase 3 Task 02",
        "run_name": run_name,
        "model_version": slo_report["model_version"],
        "alert_count": len(alerts),
        "alerts": alerts,
        "alert_status": (
            "ALERTING"
            if alerts
            else "NO_ALERT"
        ),
    }
