from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


TASK_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FIELDS = {
    "event_id",
    "candidate_id",
    "job_id",
    "event_type",
    "timestamp",
    "session_id",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def event_hash(event: Dict) -> str:
    payload = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def validate_event(event: Dict) -> Dict:
    missing = sorted(
        REQUIRED_FIELDS.difference(event.keys())
    )

    return {
        "valid": not missing,
        "missing_fields": missing,
        "event_hash": event_hash(event),
    }


def ingest_events(
    events: List[Dict],
    destination: Path,
    *,
    source_type: str,
    source_name: str,
) -> Dict:
    """
    Ingest externally captured/live events.

    source_type should be one of:
      - live_capture
      - imported_production_export
      - local_demo_seed

    The pipeline records provenance instead of falsely labeling
    synthetic/demo records as production data.
    """

    valid_events = []
    invalid_events = []

    for event in events:
        validation = validate_event(event)

        enriched = {
            **event,
            "ingested_at": utc_now(),
            "source_type": source_type,
            "source_name": source_name,
            "event_hash": validation["event_hash"],
        }

        if validation["valid"]:
            valid_events.append(enriched)
        else:
            invalid_events.append(
                {
                    "event": enriched,
                    "missing_fields": validation["missing_fields"],
                }
            )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open("w", encoding="utf-8") as handle:
        json.dump(
            valid_events,
            handle,
            indent=2,
        )

    return {
        "source_type": source_type,
        "source_name": source_name,
        "received": len(events),
        "valid": len(valid_events),
        "invalid": len(invalid_events),
        "destination": str(destination),
        "production_claim_allowed": source_type
        in {
            "live_capture",
            "imported_production_export",
        },
    }