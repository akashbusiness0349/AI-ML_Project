from __future__ import annotations

import json
from pathlib import Path

from src.fallback import popularity_fallback
from src.validation import validate_events


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
LOGS = ROOT / "logs"


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    events = load(LOGS / "live_events.json")
    candidates = load(DATA / "candidates.json")
    jobs = load(DATA / "jobs.json")
    evaluation = load(LOGS / "offline_evaluation_v4.json")
    governance = load(LOGS / "governance_audit.json")

    validation = validate_events(events)

    fallback = popularity_fallback(
        jobs,
        top_k=5,
        reason="MODEL_UNAVAILABLE_INTEGRATION_TEST",
    )

    impression_count = sum(
        1
        for event in events
        if event.get("event_type") == "impression"
    )

    click_count = sum(
        1
        for event in events
        if event.get("event_type") == "click"
    )

    apply_count = sum(
        1
        for event in events
        if event.get("event_type") == "apply"
    )

    fallback_non_empty = len(fallback) > 0

    integration_checks = {
        "events_available": len(events) > 0,
        "event_schema_valid": validation.get("valid", False),
        "cold_start_candidates_available": len(candidates) > 0,
        "jobs_available": len(jobs) > 0,
        "impressions_logged": impression_count > 0,
        "clicks_logged": click_count > 0,
        "applications_logged": apply_count > 0,
        "fallback_non_empty": fallback_non_empty,
        "heldout_evaluation_passed": (
            evaluation.get("training_and_evaluation_candidate_overlap") == 0
            and evaluation.get("recommendation_validation", {}).get("valid")
            and evaluation.get("heldout_records", 0) > 0
        ),
        "governance_audit_available": (
            governance.get("candidate_schema", {}).get("passed", False)
            and governance.get("event_schema", {}).get("passed", False)
            and not governance.get(
                "candidate_schema", {}
            ).get("protected_attributes_used_for_ranking", True)
            and governance.get("overall_schema_status", False)
        ),
    }

    status = (
        "PASS"
        if all(integration_checks.values())
        else "FAIL"
    )

    evidence = {
        "task": "PHASE_3_TASK_07",
        "title": "Activation & Onboarding Funnel Optimization",
        "integration_status": status,
        "events": len(events),
        "impressions": impression_count,
        "clicks": click_count,
        "applications": apply_count,
        "fallback_recommendations": len(fallback),
        "heldout_records": evaluation.get("heldout_records", 0),
        "model_version": evaluation.get("model_version"),
        "checks": integration_checks,
        "production_data": False,
        "notes": [
            "Integration evidence uses locally captured demonstration events.",
            "Production A/B activation lift is not measured.",
        ],
    }

    output = LOGS / "integration_signoff_v4.json"

    with output.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print("=" * 65)
    print("PHASE 3 / TASK 07 — END-TO-END INTEGRATION")
    print("=" * 65)
    print("Events                   :", len(events))
    print("Impressions              :", impression_count)
    print("Clicks                   :", click_count)
    print("Applications             :", apply_count)
    print("Fallback recommendations :", len(fallback))
    print("Event validation         :", validation.get("valid", False))
    print("Held-out evaluation      :", integration_checks["heldout_evaluation_passed"])
    print("Governance audit         :", integration_checks["governance_audit_available"])
    print("Integration status       :", status)
    print("Evidence written         :", output)
    print("=" * 65)


if __name__ == "__main__":
    main()
