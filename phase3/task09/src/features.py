from __future__ import annotations

from typing import Any
import pandas as pd


BASE_COLUMNS = [
    "entity_id",
    "entity_type",
    "event_timestamp",
    "engagement_score",
    "hiring_relevance",
    "outcome_label",
]


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Build leakage-safe event-level features.

    All activity-count features use events strictly before the
    current event timestamp for the same entity.
    """

    required = set(BASE_COLUMNS)
    missing = required - set(frame.columns)

    if missing:
        raise ValueError(
            f"Feature engineering missing columns: {sorted(missing)}"
        )

    work = frame.copy()

    work["event_timestamp"] = pd.to_datetime(
        work["event_timestamp"], utc=True, errors="raise"
    )
    work["entity_id"] = work["entity_id"].astype(str)

    work = work.sort_values(
        ["entity_id", "event_timestamp", "event_id"]
    ).reset_index(drop=True)

    result_rows: list[dict[str, Any]] = []

    for entity_id, group in work.groupby("entity_id", sort=False):
        group = group.sort_values(
            ["event_timestamp", "event_id"]
        ).reset_index(drop=True)

        timestamps = group["event_timestamp"]

        for i, row in group.iterrows():
            current_time = row["event_timestamp"]

            previous = group.iloc[:i]

            if previous.empty:
                events_1d = 0
                events_7d = 0
                events_14d = 0
                days_since_last_event = 14.0
                previous_engagement = float(row["engagement_score"])
            else:
                age_days = (
                    current_time - previous["event_timestamp"]
                ).dt.total_seconds() / 86400.0

                events_1d = int((age_days <= 1.0).sum())
                events_7d = int((age_days <= 7.0).sum())
                events_14d = int((age_days <= 14.0).sum())

                last_timestamp = previous["event_timestamp"].max()

                days_since_last_event = float(
                    (
                        current_time - last_timestamp
                    ).total_seconds() / 86400.0
                )

                previous_engagement = float(
                    previous.iloc[-1]["engagement_score"]
                )

            engagement_velocity = float(
                row["engagement_score"] - previous_engagement
            )

            activity_intensity_7d = float(
                events_7d / 7.0
            )

            result_rows.append(
                {
                    "entity_id": str(entity_id),
                    "entity_type": str(row["entity_type"]),
                    "event_timestamp": current_time,
                    "engagement_score": float(row["engagement_score"]),
                    "events_1d": events_1d,
                    "events_7d": events_7d,
                    "events_14d": events_14d,
                    "days_since_last_event": days_since_last_event,
                    "hiring_relevance": float(row["hiring_relevance"]),
                    "engagement_velocity": engagement_velocity,
                    "activity_intensity_7d": activity_intensity_7d,
                    "outcome_label": int(row["outcome_label"]),
                }
            )

    result = pd.DataFrame(result_rows)

    if result.empty:
        raise ValueError("Feature engineering produced zero rows.")

    numeric_columns = [
        "engagement_score",
        "events_1d",
        "events_7d",
        "events_14d",
        "days_since_last_event",
        "hiring_relevance",
        "engagement_velocity",
        "activity_intensity_7d",
        "outcome_label",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column], errors="raise"
        )

    return result.sort_values(
        ["event_timestamp", "entity_id"]
    ).reset_index(drop=True)
