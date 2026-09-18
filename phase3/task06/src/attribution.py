from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


OUTCOME_TYPES = {"click", "apply", "shortlist"}


def build_impression_index(
    events: Iterable[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}

    for event in events:
        if event.get("event_type") == "impression":
            index[event["impression_id"]] = event

    return index


def validate_joinability(
    events: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    events = list(events)
    impressions = build_impression_index(events)

    outcome_events = [
        event
        for event in events
        if event.get("event_type") in OUTCOME_TYPES
    ]

    joined = 0
    orphaned = []

    for event in outcome_events:
        impression_id = event.get("impression_id")

        if impression_id in impressions:
            joined += 1
        else:
            orphaned.append(event.get("event_id"))

    rate = (
        joined / len(outcome_events)
        if outcome_events
        else 1.0
    )

    return {
        "impression_count": len(impressions),
        "outcome_count": len(outcome_events),
        "joined_outcomes": joined,
        "orphaned_outcomes": len(orphaned),
        "join_rate": round(rate, 6),
        "joinable": len(orphaned) == 0,
        "orphaned_event_ids": orphaned,
    }


def reconstruct_journeys(
    events: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for event in events:
        grouped[event["impression_id"]].append(event)

    journeys = []

    for impression_id, group in grouped.items():
        group.sort(key=lambda event: event["timestamp"])

        impression = next(
            (
                event
                for event in group
                if event["event_type"] == "impression"
            ),
            None,
        )

        if impression is None:
            continue

        outcomes = [
            event["event_type"]
            for event in group
            if event["event_type"] in OUTCOME_TYPES
        ]

        journeys.append(
            {
                "impression_id": impression_id,
                "request_id": impression["request_id"],
                "ranked_list_id": impression["ranked_list_id"],
                "user_id": impression["user_id"],
                "item_id": impression["item_id"],
                "position": impression["position"],
                "model_version": impression["model_version"],
                "events": [event["event_type"] for event in group],
                "outcomes": outcomes,
                "complete_journey": [
                    "impression",
                    *outcomes,
                ],
            }
        )

    return journeys