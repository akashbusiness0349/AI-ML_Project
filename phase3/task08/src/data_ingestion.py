from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "entity_id",
    "entity_type",
    "timestamp",
    "event_type",
}

ALLOWED_ENTITY_TYPES = {
    "candidate",
    "company",
}


class DataIngestionError(ValueError):
    """Raised when event data violates the Task 08 data contract."""


def load_events(
    path: str | Path,
) -> pd.DataFrame:
    """
    Load event data from JSON.

    Expected structure:

    [
        {
            "entity_id": "candidate_001",
            "entity_type": "candidate",
            "timestamp": "2026-01-10T10:30:00Z",
            "event_type": "login"
        }
    ]
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    if path.stat().st_size == 0:
        raise DataIngestionError(
            f"Data file is empty: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            payload: Any = json.load(handle)

    except json.JSONDecodeError as exc:
        raise DataIngestionError(
            f"Invalid JSON in {path}: {exc}"
        ) from exc

    if not isinstance(
        payload,
        list,
    ):
        raise DataIngestionError(
            "Input JSON must contain an array of event objects."
        )

    if not payload:
        raise DataIngestionError(
            "Input dataset contains zero events."
        )

    dataframe = pd.DataFrame(
        payload
    )

    missing = (
        REQUIRED_COLUMNS
        - set(dataframe.columns)
    )

    if missing:
        raise DataIngestionError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    dataframe = dataframe.copy()

    dataframe["entity_id"] = (
        dataframe["entity_id"]
        .astype(str)
        .str.strip()
    )

    dataframe["entity_type"] = (
        dataframe["entity_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    dataframe["event_type"] = (
        dataframe["event_type"]
        .astype(str)
        .str.strip()
    )

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
        utc=True,
    )

    if dataframe["timestamp"].isna().any():
        count = int(
            dataframe["timestamp"].isna().sum()
        )

        raise DataIngestionError(
            f"{count} row(s) have invalid timestamps."
        )

    if dataframe["entity_id"].eq("").any():
        raise DataIngestionError(
            "entity_id cannot be empty."
        )

    if dataframe["event_type"].eq("").any():
        raise DataIngestionError(
            "event_type cannot be empty."
        )

    invalid_entity_types = sorted(
        set(dataframe["entity_type"])
        - ALLOWED_ENTITY_TYPES
    )

    if invalid_entity_types:
        raise DataIngestionError(
            "Unsupported entity_type values: "
            + ", ".join(
                invalid_entity_types
            )
        )

    dataframe = dataframe.drop_duplicates(
        subset=[
            "entity_id",
            "entity_type",
            "timestamp",
            "event_type",
        ]
    )

    dataframe = dataframe.sort_values(
        [
            "entity_id",
            "timestamp",
        ]
    ).reset_index(
        drop=True
    )

    return dataframe


def load_production_events(
    path: str | Path,
) -> pd.DataFrame:
    """
    Backward-compatible alias.

    Existing Task 08 modules can continue using this function.
    """

    return load_events(
        path
    )


def summarize_events(
    dataframe: pd.DataFrame,
) -> dict:
    if dataframe.empty:
        return {
            "rows": 0,
            "entities": 0,
            "candidates": 0,
            "companies": 0,
        }

    return {
        "rows": int(
            len(dataframe)
        ),
        "entities": int(
            dataframe["entity_id"].nunique()
        ),
        "candidate_event_rows": int(
            (
                dataframe["entity_type"]
                == "candidate"
            ).sum()
        ),
        "company_event_rows": int(
            (
                dataframe["entity_type"]
                == "company"
            ).sum()
        ),
        "unique_candidate_entities": int(
            dataframe.loc[
                dataframe["entity_type"]
                == "candidate",
                "entity_id",
            ].nunique()
        ),
        "unique_company_entities": int(
            dataframe.loc[
                dataframe["entity_type"]
                == "company",
                "entity_id",
            ].nunique()
        ),
        "first_event": dataframe[
            "timestamp"
        ].min().isoformat(),
        "last_event": dataframe[
            "timestamp"
        ].max().isoformat(),
        "event_types": sorted(
            dataframe[
                "event_type"
            ]
            .unique()
            .tolist()
        ),
    }