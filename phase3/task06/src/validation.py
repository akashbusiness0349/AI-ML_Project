from __future__ import annotations

from typing import Any, Dict, Iterable, List


REQUIRED_EVENT_FIELDS = {
    "event_id",
    "impression_id",
    "request_id",
    "ranked_list_id",
    "user_id",
    "item_id",
    "event_type",
    "position",
    "model_version",
    "timestamp",
}


def validate_event(event: Dict[str, Any]) -> Dict[str, Any]:
    missing = sorted(REQUIRED_EVENT_FIELDS - set(event.keys()))

    valid_type = event.get("event_type") in {
        "impression",
        "click",
        "apply",
        "shortlist",
    }

    valid_position = (
        isinstance(event.get("position"), int)
        and event.get("position") >= 1
    )

    valid_model = bool(event.get("model_version"))

    return {
        "valid": (
            not missing
            and valid_type
            and valid_position
            and valid_model
        ),
        "missing_fields": missing,
        "valid_event_type": valid_type,
        "valid_position": valid_position,
        "valid_model_version": valid_model,
    }


def validate_events(
    events: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    events = list(events)
    results = [validate_event(event) for event in events]

    valid = sum(
        1
        for result in results
        if result["valid"]
    )

    return {
        "total_events": len(events),
        "valid_events": valid,
        "invalid_events": len(events) - valid,
        "validation_rate": round(
            valid / len(events)
            if events
            else 0.0,
            6,
        ),
        "all_valid": bool(events) and valid == len(events),
    }


def validate_ranked_lists(
    ranked_lists: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    ranked_lists = list(ranked_lists)
    failures: List[str] = []

    for ranked_list in ranked_lists:
        results = ranked_list.get("results", [])

        positions = [
            result.get("position")
            for result in results
        ]

        expected = list(range(1, len(results) + 1))

        if positions != expected:
            failures.append(
                ranked_list.get("ranked_list_id", "unknown")
            )

        for result in results:
            if result.get("model_version") != ranked_list.get(
                "model_version"
            ):
                failures.append(
                    ranked_list.get("ranked_list_id", "unknown")
                )

    return {
        "ranked_lists": len(ranked_lists),
        "valid_ranked_lists": len(ranked_lists) - len(set(failures)),
        "invalid_ranked_lists": len(set(failures)),
        "all_positions_contiguous": not failures,
        "model_version_present_on_every_result": all(
            all(
                bool(result.get("model_version"))
                for result in ranked_list.get("results", [])
            )
            for ranked_list in ranked_lists
        ),
    }