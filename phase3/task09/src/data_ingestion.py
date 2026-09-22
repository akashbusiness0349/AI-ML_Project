from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "event_id",
    "entity_id",
    "entity_type",
    "event_timestamp",
    "event_type",
    "engagement_score",
    "hiring_relevance",
    "outcome_label",
}


NUMERIC_COLUMNS = [
    "engagement_score",
    "hiring_relevance",
    "outcome_label",
]


def load_logged_data(path: str | Path) -> pd.DataFrame:
    """
    Load event-level logged data from JSON.

    Supported JSON forms:
      1. list[dict]
      2. {"records": list[dict]}
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Logged data file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        payload: Any = json.load(handle)

    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        records = payload["records"]
    else:
        raise ValueError(
            "Expected JSON list or object containing a 'records' list."
        )

    if not records:
        raise ValueError("Logged data contains zero records.")

    frame = pd.DataFrame(records)

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(
            f"Logged data is missing required columns: {sorted(missing)}"
        )

    frame["event_timestamp"] = pd.to_datetime(
        frame["event_timestamp"],
        utc=True,
        errors="raise",
    )

    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    frame["entity_id"] = frame["entity_id"].astype(str)
    frame["entity_type"] = frame["entity_type"].astype(str)
    frame["event_type"] = frame["event_type"].astype(str)

    return frame.sort_values(
        ["event_timestamp", "entity_id", "event_id"]
    ).reset_index(drop=True)


def save_json(payload: Any, path: str | Path) -> None:
    """Write JSON using deterministic formatting."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )


def dataframe_to_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame into JSON-safe records."""
    return json.loads(frame.to_json(orient="records", date_format="iso"))