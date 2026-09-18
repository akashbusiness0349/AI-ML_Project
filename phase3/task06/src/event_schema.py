from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


EVENT_TYPES = {"impression", "click", "apply", "shortlist"}


@dataclass
class RankingEvent:
    event_id: str
    impression_id: str
    request_id: str
    ranked_list_id: str
    user_id: str
    item_id: str
    event_type: str
    position: int
    model_version: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_event(
    impression_id: str,
    request_id: str,
    ranked_list_id: str,
    user_id: str,
    item_id: str,
    event_type: str,
    position: int,
    model_version: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> RankingEvent:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")

    if position < 1:
        raise ValueError("Position must be >= 1")

    return RankingEvent(
        event_id=f"evt_{uuid4().hex}",
        impression_id=impression_id,
        request_id=request_id,
        ranked_list_id=ranked_list_id,
        user_id=user_id,
        item_id=item_id,
        event_type=event_type,
        position=position,
        model_version=model_version,
        timestamp=utc_now(),
        metadata=metadata or {},
    )