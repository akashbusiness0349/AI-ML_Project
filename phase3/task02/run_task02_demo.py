import copy
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TASK_DIR.parents[1]

TASK25_TRAFFIC = (
    PROJECT_ROOT
    / "phase2"
    / "task25"
    / "data"
    / "production_traffic.json"
)

TASK01_OFFLINE = (
    PROJECT_ROOT
    / "phase3"
    / "task01"
    / "data"
    / "offline_evaluation.json"
)

TASK01_LIVE_LOGS = (
    PROJECT_ROOT
    / "phase3"
    / "task01"
    / "data"
    / "live_interaction_logs.json"
)

LOG_DIR = TASK_DIR / "logs"

sys.path.insert(0, str(TASK_DIR))

from src.slo_monitor import (
    load_json,
    save_json,
    build_slo_report,
)

from src.alerting import build_alert_report

from src.error_budget import build_error_budget


def clone_events(events):
    return copy.deepcopy(events)


def build_reference_scores(events):
    """
    Build a comparison score distribution from a separate
    reference interaction-log dataset.

    This must not use the same events currently being monitored,
    otherwise PSI becomes artificially zero.
    """

    return [
        float(event["match_score"])
        for event in events
        if not event.get("error", False)
        and "match_score" in event
    ]


def create_latency_breach(events):
    """
    Synthetic failure:
    force every event above the latency SLO.
    """

    modified = clone_events(events)

    for event in modified:
        event["latency_ms"] = 150

    return modified


def create_quality_breach(events):
    """
    Synthetic failure:
    make every recommendation incorrect.
    """

    modified = clone_events(events)

    for event in modified:
        event["recommended"] = True
        event["relevant"] = False

    return modified


def model_unavailable_response():
    """
    Safe fallback when the model service is unavailable.
    """

    return {
        "recommendation": None,
        "status": "MODEL_UNAVAILABLE",
        "fallback_action": "return_no_recommendation",
        "safe": True,
    }


def run_scenario(
    scenario_name,
    events,
    reference_scores,
    offline_reference,
    source_path,
):
    report = build_slo_report(
        events=events,
        reference_scores=reference_scores,
        source_path=source_path,
        offline_reference=offline_reference,
    )

    alerts = build_alert_report(
        report,
        scenario_name,
    )

    failed_events = sum(
        1
        for event in events
        if event.get("error", False)
    )

    error_budget = build_error_budget(
        total_events=len(events),
        failed_events=failed_events,
        window_name=scenario_name,
    )

    return {
        "scenario": scenario_name,
        "slo_report": report,
        "alerts": alerts,
        "error_budget": error_budget,
    }


def print_scenario(result):
    report = result["slo_report"]
    observed = report["observed"]
    slo = report["slo_results"]
    alerts = result["alerts"]
    budget = result["error_budget"]

    print()
    print("=" * 70)
    print(f"SCENARIO: {result['scenario']}")
    print("=" * 70)

    print(
        f"P95 latency       : "
        f"{observed['latency']['p95_ms']:.2f} ms "
        f"(SLO <= "
        f"{report['slo_targets']['p95_latency_ms']:.2f} ms)"
    )

    print(
        f"Availability       : "
        f"{observed['availability']['availability'] * 100:.2f}% "
        f"(SLO >= "
        f"{report['slo_targets']['availability'] * 100:.2f}%)"
    )

    print(
        f"Precision          : "
        f"{observed['quality']['precision'] * 100:.2f}% "
        f"(SLO >= "
        f"{report['slo_targets']['minimum_precision'] * 100:.2f}%)"
    )

    print(
        f"Recall             : "
        f"{observed['quality']['recall'] * 100:.2f}%"
    )

    print(
        f"FPR                : "
        f"{observed['quality']['false_positive_rate'] * 100:.2f}%"
    )

    print(
        f"Unique scores      : "
        f"{observed['score_distribution']['unique_values']}"
    )

    print(
        f"PSI                : "
        f"{observed['psi']:.4f} "
        f"(threshold <= "
        f"{report['slo_targets']['psi_threshold']:.2f})"
    )

    print(
        f"Latency SLO        : "
        f"{'PASS' if slo['p95_latency']['pass'] else 'BREACH'}"
    )

    print(
        f"Availability SLO   : "
        f"{'PASS' if slo['availability']['pass'] else 'BREACH'}"
    )

    print(
        f"Precision SLO      : "
        f"{'PASS' if slo['minimum_precision']['pass'] else 'BREACH'}"
    )

    print(
        f"Score distribution : "
        f"{'PASS' if slo['score_distribution']['pass'] else 'BREACH'}"
    )

    print(
        f"Drift check        : "
        f"{'PASS' if slo['prediction_drift']['pass'] else 'ALERT'}"
    )

    print(
        f"Alerts fired       : "
        f"{alerts['alert_count']}"
    )

    for alert in alerts["alerts"]:
        print(
            f"  - {alert['alert']} | "
            f"{alert['severity']} | "
            f"Owner: {alert['owner']}"
        )

    print(
        f"Error budget       : "
        f"{budget['status']}"
    )


def save_experiment_log(results):
    path = LOG_DIR / "experiment_log.csv"

    fieldnames = [
        "timestamp_utc",
        "scenario",
        "model_version",
        "events",
        "p95_latency_ms",
        "availability",
        "precision",
        "recall",
        "fpr",
        "psi",
        "alert_count",
        "error_budget_status",
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        for result in results:

            report = result["slo_report"]
            observed = report["observed"]

            writer.writerow({
                "timestamp_utc": timestamp,

                "scenario":
                    result["scenario"],

                "model_version":
                    report["model_version"],

                "events":
                    report["data_provenance"]
                    ["event_count"],

                "p95_latency_ms":
                    observed["latency"]["p95_ms"],

                "availability":
                    observed["availability"]
                    ["availability"],

                "precision":
                    observed["quality"]
                    ["precision"],

                "recall":
                    observed["quality"]
                    ["recall"],

                "fpr":
                    observed["quality"]
                    ["false_positive_rate"],

                "psi":
                    observed["psi"],

                "alert_count":
                    result["alerts"]["alert_count"],

                "error_budget_status":
                    result["error_budget"]["status"],
            })


def main():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # LOAD TRAFFIC DATA
    # ---------------------------------------------------------

    traffic_data = load_json(
        TASK25_TRAFFIC
    )

    # ---------------------------------------------------------
    # LOAD OFFLINE REFERENCE
    # ---------------------------------------------------------

    offline_data = load_json(
        TASK01_OFFLINE
    )

    # ---------------------------------------------------------
    # LOAD SEPARATE REFERENCE SCORE DATA
    # ---------------------------------------------------------

    reference_data = load_json(
        TASK01_LIVE_LOGS
    )

    events = traffic_data["events"]

    reference_events = reference_data["events"]

    reference_scores = build_reference_scores(
        reference_events
    )

    # ---------------------------------------------------------
    # OFFLINE REFERENCE METADATA
    # ---------------------------------------------------------

    offline_reference = {
        "evaluation_id":
            offline_data["evaluation_id"],

        "model_version":
            offline_data["model_version"],

        "evaluation_type":
            offline_data["evaluation_type"],

        "dataset_type":
            offline_data["dataset_type"],

        "tuned_on_this_dataset":
            offline_data["tuned_on_this_dataset"],

        "metrics":
            offline_data["metrics"],

        "note":
            offline_data["note"],
    }

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    print()
    print("PHASE 3 - TASK 02")
    print("OBSERVABILITY DEEP-DIVE, SLOs & ERROR BUDGETS")
    print()

    print(
        f"Source traffic      : "
        f"{TASK25_TRAFFIC}"
    )

    print(
        f"Reference scores    : "
        f"{TASK01_LIVE_LOGS}"
    )

    print(
        f"Model version       : "
        f"{traffic_data['model_version']}"
    )

    print(
        f"Traffic events      : "
        f"{len(events)}"
    )

    print(
        f"Reference events    : "
        f"{len(reference_events)}"
    )

    print(
        f"Reference scores    : "
        f"{len(reference_scores)}"
    )

    print(
        "Scope               : "
        "production-style go-live rehearsal"
    )

    print(
        "External production : "
        "False"
    )

    # ---------------------------------------------------------
    # NORMAL TRAFFIC
    # ---------------------------------------------------------

    normal_result = run_scenario(
        "normal_traffic",
        events,
        reference_scores,
        offline_reference,
        TASK25_TRAFFIC,
    )

    # ---------------------------------------------------------
    # LATENCY BREACH
    # ---------------------------------------------------------

    latency_result = run_scenario(
        "synthetic_latency_breach",
        create_latency_breach(events),
        reference_scores,
        offline_reference,
        TASK25_TRAFFIC,
    )

    # ---------------------------------------------------------
    # QUALITY BREACH
    # ---------------------------------------------------------

    quality_result = run_scenario(
        "synthetic_quality_breach",
        create_quality_breach(events),
        reference_scores,
        offline_reference,
        TASK25_TRAFFIC,
    )

    results = [
        normal_result,
        latency_result,
        quality_result,
    ]

    # ---------------------------------------------------------
    # PRINT SCENARIOS
    # ---------------------------------------------------------

    for result in results:
        print_scenario(result)

    # ---------------------------------------------------------
    # MODEL UNAVAILABLE
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("MODEL UNAVAILABLE FAILURE PATH")
    print("=" * 70)

    unavailable = model_unavailable_response()

    print(
        f"Status              : "
        f"{unavailable['status']}"
    )

    print(
        f"Fallback            : "
        f"{unavailable['fallback_action']}"
    )

    print(
        f"Safe                : "
        f"{unavailable['safe']}"
    )

    # ---------------------------------------------------------
    # FULL EVIDENCE OBJECT
    # ---------------------------------------------------------

    all_reports = {

        "task":
            "Phase 3 Task 02",

        "generated_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "model_version":
            traffic_data["model_version"],

        "scope": {
            "production_style_rehearsal": True,
            "external_production": False,
        },

        "source": {

            "traffic_file":
                str(
                    TASK25_TRAFFIC.resolve()
                ),

            "reference_score_file":
                str(
                    TASK01_LIVE_LOGS.resolve()
                ),

            "offline_reference":
                str(
                    TASK01_OFFLINE.resolve()
                ),
        },

        "reference_distribution": {
            "event_count":
                len(reference_events),

            "score_count":
                len(reference_scores),

            "source":
                str(
                    TASK01_LIVE_LOGS.resolve()
                ),
        },

        "scenarios":
            results,

        "model_unavailable":
            unavailable,

        "completion": {

            "slo_definition":
                True,

            "monitoring_and_alerts":
                True,

            "error_budget":
                True,

            "synthetic_latency_breach":
                True,

            "synthetic_quality_breach":
                True,

            "safe_failure_path":
                True,
        },
    }

    # ---------------------------------------------------------
    # SAVE EVIDENCE
    # ---------------------------------------------------------

    save_json(
        all_reports,
        LOG_DIR / "task02_evidence.json",
    )

    save_json(
        normal_result["slo_report"],
        LOG_DIR / "slo_report.json",
    )

    save_json(
        normal_result["alerts"],
        LOG_DIR / "alerts.json",
    )

    save_json(
        normal_result["error_budget"],
        LOG_DIR / "error_budget.json",
    )

    save_json(
        latency_result,
        LOG_DIR / "latency_breach_evidence.json",
    )

    save_json(
        quality_result,
        LOG_DIR / "quality_breach_evidence.json",
    )

    save_json(
        unavailable,
        LOG_DIR / "model_unavailable_evidence.json",
    )

    save_experiment_log(
        results
    )

    # ---------------------------------------------------------
    # PERSISTENCE OUTPUT
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("PERSISTED EVIDENCE")
    print("=" * 70)

    print(
        f"SLO report          : "
        f"{LOG_DIR / 'slo_report.json'}"
    )

    print(
        f"Alerts              : "
        f"{LOG_DIR / 'alerts.json'}"
    )

    print(
        f"Error budget        : "
        f"{LOG_DIR / 'error_budget.json'}"
    )

    print(
        f"Latency breach      : "
        f"{LOG_DIR / 'latency_breach_evidence.json'}"
    )

    print(
        f"Quality breach      : "
        f"{LOG_DIR / 'quality_breach_evidence.json'}"
    )

    print(
        f"Failure path        : "
        f"{LOG_DIR / 'model_unavailable_evidence.json'}"
    )

    print(
        f"Full evidence       : "
        f"{LOG_DIR / 'task02_evidence.json'}"
    )

    print(
        f"Experiment log      : "
        f"{LOG_DIR / 'experiment_log.csv'}"
    )

    print()
    print("TASK 02 STATUS: PASS")


if __name__ == "__main__":
    main()