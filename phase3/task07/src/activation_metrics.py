"""
Task 07 — Activation & Onboarding Metrics
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def _candidate_ids(events: list[dict[str, Any]]) -> set[str]:
    return {
        str(event.get("candidate_id"))
        for event in events
        if event.get("candidate_id")
    }


def activation_rate(events: list[dict[str, Any]]) -> float:
    """
    Activation = candidate generated an application event.
    """

    candidates = _candidate_ids(events)

    if not candidates:
        return 0.0

    activated = {
        str(event.get("candidate_id"))
        for event in events
        if event.get("event_type") == "apply"
    }

    return len(activated & candidates) / len(candidates)


def event_rate(
    events: list[dict[str, Any]],
    event_type: str,
) -> float:
    candidates = _candidate_ids(events)

    if not candidates:
        return 0.0

    users_with_event = {
        str(event.get("candidate_id"))
        for event in events
        if event.get("event_type") == event_type
    }

    return len(users_with_event & candidates) / len(candidates)


def funnel_counts(
    events: list[dict[str, Any]],
) -> dict[str, int]:
    counts = Counter(
        str(event.get("event_type"))
        for event in events
        if event.get("event_type")
    )

    return dict(counts)


def experiment_metrics(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates = _candidate_ids(events)

    clicks = {
        str(event.get("candidate_id"))
        for event in events
        if event.get("event_type") == "click"
    }

    applications = {
        str(event.get("candidate_id"))
        for event in events
        if event.get("event_type") == "apply"
    }

    impressions = {
        str(event.get("candidate_id"))
        for event in events
        if event.get("event_type") == "impression"
    }

    return {
        "unique_candidates": len(candidates),
        "impression_users": len(impressions),
        "click_users": len(clicks),
        "application_users": len(applications),
        "activation_rate": (
            len(applications & candidates) / len(candidates)
            if candidates
            else 0.0
        ),
        "click_rate": (
            len(clicks & candidates) / len(candidates)
            if candidates
            else 0.0
        ),
        "click_to_apply_rate": (
            len(applications & clicks) / len(clicks)
            if clicks
            else 0.0
        ),
        "event_counts": funnel_counts(events),
    }


def compare_experiment_groups(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}

    for event in events:
        group = str(event.get("experiment_group", "unknown"))
        groups.setdefault(group, []).append(event)

    result: dict[str, Any] = {}

    for group, group_events in sorted(groups.items()):
        result[group] = experiment_metrics(group_events)

    return result


def evaluate_ranking(
    recommendations: list[dict[str, Any]],
    relevant_jobs: list[str],
    k: int = 5,
) -> dict[str, float]:
    relevant = {
        str(job_id)
        for job_id in relevant_jobs
    }

    top = recommendations[:k]

    if not top:
        return {
            "precision_at_k": 0.0,
            "recall_at_k": 0.0,
            "ndcg_at_k": 0.0,
        }

    hits = [
        1 if str(item.get("job_id")) in relevant else 0
        for item in top
    ]

    precision = sum(hits) / len(hits)

    recall = (
        sum(hits) / len(relevant)
        if relevant
        else 0.0
    )

    dcg = sum(
        hit / __import__("math").log2(index + 2)
        for index, hit in enumerate(hits)
    )

    ideal_hits = [1] * min(len(relevant), k)

    idcg = sum(
        hit / __import__("math").log2(index + 2)
        for index, hit in enumerate(ideal_hits)
    )

    ndcg = dcg / idcg if idcg else 0.0

    return {
        "precision_at_k": round(precision, 6),
        "recall_at_k": round(recall, 6),
        "ndcg_at_k": round(ndcg, 6),
    }