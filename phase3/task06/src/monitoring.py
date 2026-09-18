from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


def calculate_metrics(
    events: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    events = list(events)

    counts = {
        "impressions": 0,
        "clicks": 0,
        "applications": 0,
        "shortlists": 0,
    }

    for event in events:
        event_type = event.get("event_type")

        if event_type == "impression":
            counts["impressions"] += 1
        elif event_type == "click":
            counts["clicks"] += 1
        elif event_type == "apply":
            counts["applications"] += 1
        elif event_type == "shortlist":
            counts["shortlists"] += 1

    impressions = counts["impressions"]

    ctr = counts["clicks"] / impressions if impressions else 0.0
    apply_rate = (
        counts["applications"] / impressions
        if impressions
        else 0.0
    )
    shortlist_rate = (
        counts["shortlists"] / impressions
        if impressions
        else 0.0
    )
    click_to_apply = (
        counts["applications"] / counts["clicks"]
        if counts["clicks"]
        else 0.0
    )
    apply_to_shortlist = (
        counts["shortlists"] / counts["applications"]
        if counts["applications"]
        else 0.0
    )

    return {
        **counts,
        "click_through_rate": round(ctr, 6),
        "apply_through_rate": round(apply_rate, 6),
        "shortlist_through_rate": round(shortlist_rate, 6),
        "click_to_apply_rate": round(click_to_apply, 6),
        "apply_to_shortlist_rate": round(
            apply_to_shortlist,
            6,
        ),
    }


def calculate_position_metrics(
    events: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    grouped: Dict[int, Dict[str, int]] = defaultdict(
        lambda: {
            "impressions": 0,
            "clicks": 0,
            "applications": 0,
            "shortlists": 0,
        }
    )

    for event in events:
        position = event.get("position")

        if not isinstance(position, int):
            continue

        event_type = event.get("event_type")
        key = grouped[position]

        if event_type == "impression":
            key["impressions"] += 1
        elif event_type == "click":
            key["clicks"] += 1
        elif event_type == "apply":
            key["applications"] += 1
        elif event_type == "shortlist":
            key["shortlists"] += 1

    output = []

    for position in sorted(grouped):
        row = grouped[position]
        impressions = row["impressions"]

        output.append(
            {
                "position": position,
                **row,
                "click_rate": round(
                    row["clicks"] / impressions
                    if impressions
                    else 0.0,
                    6,
                ),
                "apply_rate": round(
                    row["applications"] / impressions
                    if impressions
                    else 0.0,
                    6,
                ),
                "shortlist_rate": round(
                    row["shortlists"] / impressions
                    if impressions
                    else 0.0,
                    6,
                ),
            }
        )

    return output