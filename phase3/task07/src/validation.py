"""
Task 07 — Validation utilities
"""

from __future__ import annotations

from typing import Any


def validate_candidate(
    candidate: dict[str, Any],
) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not candidate.get("candidate_id"):
        errors.append("candidate_id is required")

    if not isinstance(candidate.get("skills", []), list):
        errors.append("skills must be a list")

    if not candidate.get("experience_level"):
        errors.append("experience_level is required")

    if not candidate.get("location"):
        errors.append("location is required")

    return len(errors) == 0, errors


def validate_recommendation(
    recommendation: dict[str, Any],
) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not recommendation.get("job_id"):
        errors.append("job_id is required")

    score = recommendation.get("score")

    if not isinstance(score, (int, float)):
        errors.append("score must be numeric")

    if isinstance(score, (int, float)):
        if score < 0:
            errors.append("score cannot be negative")

    return len(errors) == 0, errors


def validate_events(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    allowed_events = {
        "impression",
        "click",
        "apply",
        "shortlist",
        "dismiss",
        "skip",
    }

    for index, event in enumerate(events):
        if not event.get("candidate_id"):
            errors.append(
                {
                    "index": index,
                    "error": "candidate_id is required",
                }
            )

        if not event.get("job_id"):
            errors.append(
                {
                    "index": index,
                    "error": "job_id is required",
                }
            )

        if event.get("event_type") not in allowed_events:
            errors.append(
                {
                    "index": index,
                    "error": "invalid event_type",
                }
            )

    return {
        "valid": len(errors) == 0,
        "event_count": len(events),
        "error_count": len(errors),
        "errors": errors,
    }


def validate_recommendations(
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    for index, recommendation in enumerate(recommendations):
        valid, item_errors = validate_recommendation(
            recommendation
        )

        if not valid:
            errors.append(
                {
                    "index": index,
                    "errors": item_errors,
                }
            )

    return {
        "valid": len(errors) == 0,
        "recommendation_count": len(recommendations),
        "error_count": len(errors),
        "errors": errors,
    }