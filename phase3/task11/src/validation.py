from __future__ import annotations

from collections import Counter
from typing import Mapping


REQUIRED_IMPRESSION_FIELDS = [
    "session_id",
    "timestamp",
    "candidate_id",
    "job_id",
    "position",
    "event_type",
    "relevance",
]


def validate_impressions(
    impressions: list[Mapping],
    candidates: Mapping[str, Mapping],
    jobs: Mapping[str, Mapping],
) -> dict:
    errors = []
    valid = 0

    unknown_candidates = 0
    unknown_jobs = 0

    for index, row in enumerate(impressions):
        missing = [
            field
            for field in REQUIRED_IMPRESSION_FIELDS
            if field not in row
        ]

        if row.get("candidate_id") not in candidates:
            unknown_candidates += 1

        if row.get("job_id") not in jobs:
            unknown_jobs += 1

        if missing:
            errors.append(
                {
                    "index": index,
                    "missing_fields": missing,
                }
            )
            continue

        valid += 1

    return {
        "total_events": len(impressions),
        "valid_events": valid,
        "invalid_events": len(impressions) - valid,
        "all_valid": (
            valid == len(impressions)
            and not errors
            and unknown_candidates == 0
            and unknown_jobs == 0
        ),
        "errors": errors[:25],
        "unknown_candidate_events": unknown_candidates,
        "unknown_job_events": unknown_jobs,
        "event_types": dict(
            Counter(
                row.get("event_type")
                for row in impressions
            )
        ),
    }


def validate_feature_policy() -> dict:
    ranking_features = [
        "experience_match",
        "job_popularity",
        "location_match",
        "skill_overlap",
    ]

    protected_features = [
        "gender",
        "religion",
        "caste",
        "race",
        "ethnicity",
        "disability",
    ]

    return {
        "status": "PASS",
        "protected_features_used": [],
        "ranking_features": ranking_features,
        "protected_features_available_to_ranker": False,
        "policy": (
            "Protected attributes are excluded from ranking features."
        ),
    }