from __future__ import annotations

from typing import Any

import pandas as pd

from .data_ingestion import REQUIRED_COLUMNS


ALLOWED_ENTITY_TYPES = {"candidate", "company"}


def validate_logged_data(frame: pd.DataFrame) -> dict[str, Any]:
    """
    Validate the Task 09 logged-data contract.

    hiring_relevance is intentionally a continuous [0, 1] score.
    outcome_label is the binary target.
    """
    errors: list[str] = []
    warnings: list[str] = []

    missing = REQUIRED_COLUMNS - set(frame.columns)

    if missing:
        errors.append(
            f"Missing columns: {sorted(missing)}"
        )

    if frame.empty:
        errors.append("Dataset is empty.")
        return _build_result(
            frame,
            errors,
            warnings,
        )

    if frame["event_id"].duplicated().any():
        errors.append(
            "Duplicate event_id values detected."
        )

    if frame["entity_id"].isna().any():
        errors.append(
            "Null entity_id values detected."
        )

    invalid_entity_types = set(
        frame.loc[
            ~frame["entity_type"].isin(
                ALLOWED_ENTITY_TYPES
            ),
            "entity_type",
        ]
    )

    if invalid_entity_types:
        errors.append(
            "Invalid entity_type values: "
            f"{sorted(invalid_entity_types)}"
        )

    if frame["event_timestamp"].isna().any():
        errors.append(
            "Null event_timestamp values detected."
        )

    # ---------------------------------------------------------
    # engagement_score
    # ---------------------------------------------------------
    if frame["engagement_score"].isna().any():
        errors.append(
            "Null engagement_score values detected."
        )

    if (
        (frame["engagement_score"] < 0)
        | (frame["engagement_score"] > 1)
    ).any():
        errors.append(
            "engagement_score must be within [0, 1]."
        )

    # ---------------------------------------------------------
    # hiring_relevance
    # ---------------------------------------------------------
    # This is a continuous relevance score, NOT a binary field.
    if frame["hiring_relevance"].isna().any():
        errors.append(
            "Null hiring_relevance values detected."
        )

    if (
        (frame["hiring_relevance"] < 0)
        | (frame["hiring_relevance"] > 1)
    ).any():
        errors.append(
            "hiring_relevance must be within [0, 1]."
        )

    # ---------------------------------------------------------
    # outcome_label
    # ---------------------------------------------------------
    if frame["outcome_label"].isna().any():
        errors.append(
            "Null outcome_label values detected."
        )

    invalid_labels = set(
        frame["outcome_label"].dropna().unique()
    ) - {0, 1}

    if invalid_labels:
        errors.append(
            "outcome_label must contain only 0/1 values; "
            f"found {sorted(invalid_labels)}"
        )

    # ---------------------------------------------------------
    # Dataset-size warnings
    # ---------------------------------------------------------
    unique_entities = frame["entity_id"].nunique()

    if unique_entities < 20:
        warnings.append(
            "Fewer than 20 unique entities. "
            "This is unsuitable for production experimentation "
            "and is only appropriate for a demo fixture."
        )

    if frame["event_timestamp"].min() == frame["event_timestamp"].max():
        warnings.append(
            "All events have the same timestamp."
        )

    return _build_result(
        frame,
        errors,
        warnings,
    )


def _build_result(
    frame: pd.DataFrame,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "status": "FAIL" if errors else "PASS",
        "rows": int(len(frame)),
        "unique_entities": (
            int(frame["entity_id"].nunique())
            if "entity_id" in frame.columns
            else 0
        ),
        "unique_events": (
            int(frame["event_id"].nunique())
            if "event_id" in frame.columns
            else 0
        ),
        "date_min": (
            str(frame["event_timestamp"].min())
            if not frame.empty
            and "event_timestamp" in frame.columns
            else None
        ),
        "date_max": (
            str(frame["event_timestamp"].max())
            if not frame.empty
            and "event_timestamp" in frame.columns
            else None
        ),
        "errors": errors,
        "warnings": warnings,
    }
