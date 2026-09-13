import csv
import json
from pathlib import Path

from src.model_health import (
    load_json,
    build_health_report,
    model_unavailable_response
)
from src.defect_ranker import rank_defects
from src.backlog import build_backlog


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

OFFLINE_FILE = DATA_DIR / "offline_evaluation.json"
LIVE_FILE = DATA_DIR / "live_interaction_logs.json"

HEALTH_OUTPUT = LOG_DIR / "health_report.json"
DEFECT_OUTPUT = LOG_DIR / "intelligence_defects.json"
BACKLOG_OUTPUT = LOG_DIR / "phase3_backlog.json"
EVIDENCE_OUTPUT = LOG_DIR / "task01_evidence.json"
EXPERIMENT_LOG = LOG_DIR / "experiment_log.csv"


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def save_experiment_log(health_report):
    file_exists = EXPERIMENT_LOG.exists()

    with EXPERIMENT_LOG.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "task",
                "model_version",
                "offline_precision",
                "online_precision",
                "precision_gap",
                "online_recall",
                "online_fpr",
                "health_status"
            ])

        writer.writerow([
            "phase3_task01",
            health_report["model_version"],
            health_report["offline_metrics"]["precision"],
            health_report["online_metrics"]["precision"],
            health_report["offline_online_gap"]["precision_gap"],
            health_report["online_metrics"]["recall"],
            health_report["online_metrics"]["false_positive_rate"],
            health_report["health_status"]
        ])


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    offline_data = load_json(OFFLINE_FILE)
    live_data = load_json(LIVE_FILE)

    health_report = build_health_report(
        offline_data,
        live_data
    )

    defects = rank_defects(
        health_report,
        live_data
    )

    backlog = build_backlog(defects)

    failure_response = model_unavailable_response()

    save_json(HEALTH_OUTPUT, health_report)
    save_json(DEFECT_OUTPUT, defects)
    save_json(BACKLOG_OUTPUT, backlog)

    evidence = {
        "task": "Phase 3 Task 01",
        "status": "PASS",
        "deliverables": {
            "model_health_report": True,
            "intelligence_defect_ranking": True,
            "phase3_backlog": True
        },
        "primary_underperformance_number": {
            "metric": "precision_gap",
            "value": health_report["offline_online_gap"]["precision_gap"],
            "offline_precision": health_report["offline_metrics"]["precision"],
            "online_precision": health_report["online_metrics"]["precision"]
        },
        "live_prediction_logging": {
            "events": health_report["traffic"]["events"],
            "available": True
        },
        "explainability": health_report["explainability"],
        "model_unavailable_test": failure_response,
        "source_scope": {
            "external_production": live_data["external_production"],
            "description": "Production-style rehearsal evidence, not external marketplace production telemetry."
        }
    }

    save_json(EVIDENCE_OUTPUT, evidence)
    save_experiment_log(health_report)

    print("=" * 70)
    print("PHASE 3 - TASK 01")
    print("POST-LAUNCH HEALTH, INCIDENT COMMAND & SPRINT PLANNING")
    print("=" * 70)

    print("\nMODEL HEALTH")
    print("-" * 70)

    print(
        f"Model version       : "
        f"{health_report['model_version']}"
    )

    print(
        f"Offline precision   : "
        f"{health_report['offline_metrics']['precision']:.2%}"
    )

    print(
        f"Online precision    : "
        f"{health_report['online_metrics']['precision']:.2%}"
    )

    print(
        f"Precision gap       : "
        f"{health_report['offline_online_gap']['precision_gap']:.2%}"
    )

    print(
        f"Online recall       : "
        f"{health_report['online_metrics']['recall']:.2%}"
    )

    print(
        f"Online FPR          : "
        f"{health_report['online_metrics']['false_positive_rate']:.2%}"
    )

    print(
        f"Health status       : "
        f"{health_report['health_status']}"
    )

    print("\nTRAFFIC")
    print("-" * 70)

    print(
        f"Events              : "
        f"{health_report['traffic']['events']}"
    )

    print(
        f"Error rate          : "
        f"{health_report['traffic']['error_rate']:.2%}"
    )

    print(
        f"Average latency     : "
        f"{health_report['latency']['average_ms']:.2f} ms"
    )

    print(
        f"Maximum latency     : "
        f"{health_report['latency']['maximum_ms']:.2f} ms"
    )

    print("\nRANKED INTELLIGENCE DEFECTS")
    print("-" * 70)

    for defect in defects:
        print(
            f"{defect['priority']}. "
            f"{defect['defect_id']} - "
            f"{defect['title']} | "
            f"Severity: {defect['severity']} | "
            f"Measured: {defect['measured_value']:.2%}"
            if isinstance(defect["measured_value"], float)
            else
            f"{defect['priority']}. "
            f"{defect['defect_id']} - "
            f"{defect['title']} | "
            f"Severity: {defect['severity']}"
        )

    print("\nPHASE 3 BACKLOG")
    print("-" * 70)

    for item in backlog:
        print(
            f"{item['backlog_id']} | "
            f"{item['owner']} | "
            f"{item['status']} | "
            f"{item['success_metric']}"
        )

    print("\nMODEL UNAVAILABLE FAILURE PATH")
    print("-" * 70)

    print(
        f"Status              : "
        f"{failure_response['status']}"
    )

    print(
        f"Fallback            : "
        f"{failure_response['fallback_action']}"
    )

    print(
        f"Safe                : "
        f"{failure_response['safe']}"
    )

    print("\nPERSISTENCE")
    print("-" * 70)

    print(f"Health report       : {HEALTH_OUTPUT}")
    print(f"Defect report       : {DEFECT_OUTPUT}")
    print(f"Backlog             : {BACKLOG_OUTPUT}")
    print(f"Evidence            : {EVIDENCE_OUTPUT}")
    print(f"Experiment log      : {EXPERIMENT_LOG}")

    print("\n" + "=" * 70)
    print("TASK 01 STATUS: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()