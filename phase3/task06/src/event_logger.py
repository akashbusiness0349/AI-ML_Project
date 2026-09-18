from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .event_schema import create_event


class EventLogger:
    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def log(
        self,
        impression_id: str,
        request_id: str,
        ranked_list_id: str,
        user_id: str,
        item_id: str,
        event_type: str,
        position: int,
        model_version: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event = create_event(
            impression_id=impression_id,
            request_id=request_id,
            ranked_list_id=ranked_list_id,
            user_id=user_id,
            item_id=item_id,
            event_type=event_type,
            position=position,
            model_version=model_version,
            metadata=metadata,
        ).to_dict()

        self.events.append(event)
        return event

    def log_ranked_list(
        self,
        ranked_list: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        results = ranked_list["results"]

        for result in results:
            impression_id = (
                f"imp_{ranked_list['ranked_list_id']}_{result['position']}"
            )

            self.log(
                impression_id=impression_id,
                request_id=ranked_list["request_id"],
                ranked_list_id=ranked_list["ranked_list_id"],
                user_id=ranked_list["user_id"],
                item_id=result["item_id"],
                event_type="impression",
                position=result["position"],
                model_version=result["model_version"],
                metadata={
                    "ranking_score": result["score"]
                },
            )

        return self.events

    def log_outcome(
        self,
        impression_id: str,
        request_id: str,
        ranked_list_id: str,
        user_id: str,
        item_id: str,
        event_type: str,
        position: int,
        model_version: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return self.log(
            impression_id=impression_id,
            request_id=request_id,
            ranked_list_id=ranked_list_id,
            user_id=user_id,
            item_id=item_id,
            event_type=event_type,
            position=position,
            model_version=model_version,
            metadata=metadata,
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.events, indent=2),
            encoding="utf-8",
        )


def load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        records = data.get("events")
        if isinstance(records, list):
            return records

    return []


def count_events(events: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts = {
        "impression": 0,
        "click": 0,
        "apply": 0,
        "shortlist": 0,
    }

    for event in events:
        event_type = event.get("event_type")
        if event_type in counts:
            counts[event_type] += 1

    return counts