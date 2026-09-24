from __future__ import annotations

import json

from src.data import (
    load_candidates,
    load_impressions,
    load_jobs,
    save_json,
)
from src.validation import (
    validate_feature_policy,
    validate_impressions,
)


def main() -> None:
    candidates = load_candidates()
    jobs = load_jobs()
    impressions = load_impressions()

    candidate_map = {
        row["candidate_id"]: row
        for row in candidates
    }

    job_map = {
        row["job_id"]: row
        for row in jobs
    }

    event_validation = validate_impressions(
        impressions,
        candidate_map,
        job_map,
    )

    feature_policy = (
        validate_feature_policy()
    )

    result = {
        "task": "Phase 3 Task 11",
        "status": (
            "PASS"
            if event_validation["all_valid"]
            and feature_policy["status"] == "PASS"
            else "FAIL"
        ),
        "candidate_count": len(candidates),
        "job_count": len(jobs),
        "impression_events": len(
            impressions
        ),
        "event_validation": event_validation,
        "feature_policy": feature_policy,
        "data_source": (
            "task11_owned_synthetic_logged_impressions"
        ),
        "production_evidence_status": (
            "NOT_PRODUCTION_EVIDENCE"
        ),
    }

    save_json(
        result,
        "logs/data_validation.json",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()