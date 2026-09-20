from __future__ import annotations

import numpy as np
import pandas as pd

from .labeling import LabelConfig
from .validation import assert_no_future_events


FEATURE_COLUMNS = [
    "event_count_14d",
    "active_days_14d",
    "days_since_last_activity",
    "event_type_diversity_14d",
    "recent_3d_events",
    "recent_7d_events",
    "activity_rate_14d",
]


def _features_for_prediction_point(
    entity_events: pd.DataFrame,
    prediction_time: pd.Timestamp,
    config: LabelConfig,
) -> dict:
    lookback_start = (
        prediction_time
        - pd.Timedelta(days=config.lookback_days)
    )

    window = entity_events[
        (entity_events["timestamp"] > lookback_start)
        & (entity_events["timestamp"] <= prediction_time)
    ].copy()

    assert_no_future_events(
        prediction_time,
        window,
    )

    if window.empty:
        return {
            "event_count_14d": 0,
            "active_days_14d": 0,
            "days_since_last_activity": float(
                config.lookback_days
            ),
            "event_type_diversity_14d": 0,
            "recent_3d_events": 0,
            "recent_7d_events": 0,
            "activity_rate_14d": 0.0,
        }

    last_activity = window["timestamp"].max()

    days_since_last_activity = max(
        0.0,
        (
            prediction_time - last_activity
        ).total_seconds() / 86400.0,
    )

    recent_3d_start = (
        prediction_time
        - pd.Timedelta(days=3)
    )

    recent_7d_start = (
        prediction_time
        - pd.Timedelta(days=7)
    )

    recent_3d = window[
        window["timestamp"] > recent_3d_start
    ]

    recent_7d = window[
        window["timestamp"] > recent_7d_start
    ]

    active_days = window["timestamp"].dt.date.nunique()

    return {
        "event_count_14d": int(len(window)),
        "active_days_14d": int(active_days),
        "days_since_last_activity": float(
            days_since_last_activity
        ),
        "event_type_diversity_14d": int(
            window["event_type"].nunique()
        ),
        "recent_3d_events": int(len(recent_3d)),
        "recent_7d_events": int(len(recent_7d)),
        "activity_rate_14d": float(
            len(window) / config.lookback_days
        ),
    }


def build_feature_table(
    events: pd.DataFrame,
    labels: pd.DataFrame,
    config: LabelConfig | None = None,
) -> pd.DataFrame:
    """
    Construct features using only events available at prediction time.
    """

    config = config or LabelConfig()

    rows: list[dict] = []

    for row in labels.itertuples(index=False):
        entity_events = events[
            events["entity_id"] == row.entity_id
        ].copy()

        feature_values = _features_for_prediction_point(
            entity_events,
            row.prediction_time,
            config,
        )

        record = {
            "entity_id": row.entity_id,
            "entity_type": row.entity_type,
            "prediction_time": row.prediction_time,
            "future_horizon_end": row.future_horizon_end,
            "churn_label": int(row.churn_label),
        }

        record.update(feature_values)

        rows.append(record)

    dataframe = pd.DataFrame(rows)

    if dataframe.empty:
        raise ValueError("Feature table is empty.")

    for column in FEATURE_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe[FEATURE_COLUMNS] = (
        dataframe[FEATURE_COLUMNS]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )

    return dataframe.sort_values(
        "prediction_time"
    ).reset_index(drop=True)


def get_feature_columns() -> list[str]:
    return FEATURE_COLUMNS.copy()