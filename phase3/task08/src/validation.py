from __future__ import annotations

from typing import Iterable

import pandas as pd


SENSITIVE_FIELD_NAMES = {
    "gender",
    "sex",
    "religion",
    "race",
    "caste",
    "ethnicity",
    "disability",
    "age",
    "date_of_birth",
    "dob",
    "health",
    "medical",
}


def validate_event_dataframe(dataframe: pd.DataFrame) -> list[str]:
    """
    Validate the production event dataframe.

    Returns a list of validation errors.
    An empty list means the dataframe passed structural validation.
    """

    errors: list[str] = []

    required = {
        "entity_id",
        "entity_type",
        "timestamp",
        "event_type",
    }

    missing = required - set(dataframe.columns)

    if missing:
        errors.append(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    if dataframe.empty:
        errors.append("Dataset contains zero rows.")
        return errors

    if "entity_id" in dataframe.columns:
        if dataframe["entity_id"].isna().any():
            errors.append("entity_id contains null values.")

    if "timestamp" in dataframe.columns:
        if not pd.api.types.is_datetime64_any_dtype(
            dataframe["timestamp"]
        ):
            errors.append(
                "timestamp must be converted to a datetime dtype."
            )

    if "entity_type" in dataframe.columns:
        allowed = {"candidate", "company"}
        invalid = set(dataframe["entity_type"].dropna().unique()) - allowed

        if invalid:
            errors.append(
                "Unsupported entity_type values: "
                + ", ".join(sorted(map(str, invalid)))
            )

    return errors


def detect_sensitive_fields(
    columns: Iterable[str],
) -> list[str]:
    """
    Identify fields that should not be used by the predictive model.
    """

    detected: list[str] = []

    for column in columns:
        normalized = (
            str(column)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized in SENSITIVE_FIELD_NAMES:
            detected.append(str(column))

    return sorted(set(detected))


def detect_target_leakage(
    feature_columns: Iterable[str],
) -> list[str]:
    """
    Conservative feature-name leakage check.

    This is a guardrail, not proof of absence of leakage.
    Temporal feature construction is responsible for the main
    leakage prevention.
    """

    suspicious_tokens = {
        "churned",
        "churn",
        "future",
        "outcome",
        "label",
        "target",
        "cancelled",
        "canceled",
        "retained",
        "retention_outcome",
    }

    suspicious: list[str] = []

    for column in feature_columns:
        normalized = str(column).lower()

        if any(token in normalized for token in suspicious_tokens):
            suspicious.append(str(column))

    return sorted(set(suspicious))


def validate_feature_columns(
    feature_columns: Iterable[str],
) -> None:
    """Raise an error if obvious target leakage is detected."""

    leakage = detect_target_leakage(feature_columns)

    if leakage:
        raise ValueError(
            "Potential target leakage detected in feature columns: "
            + ", ".join(leakage)
        )


def assert_no_future_events(
    feature_time: pd.Timestamp,
    feature_events: pd.DataFrame,
) -> None:
    """
    Strict temporal guardrail.

    Every feature event must occur at or before prediction time.
    """

    if feature_events.empty:
        return

    future_rows = feature_events[
        feature_events["timestamp"] > feature_time
    ]

    if not future_rows.empty:
        raise ValueError(
            "Target leakage detected: feature window contains "
            f"{len(future_rows)} event(s) after prediction time "
            f"{feature_time.isoformat()}."
        )