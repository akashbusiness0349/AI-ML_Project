from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class LabelConfig:
    """
    Temporal churn definition.

    Prediction time:
        T

    Feature lookback:
        T - 14 days through T

    Churn horizon:
        T through T + 14 days

    Churn:
        1 if no qualifying future activity exists
        during the complete future horizon.

        0 if at least one qualifying future activity exists.
    """

    lookback_days: int = 14
    horizon_days: int = 14


def create_prediction_points(
    events: pd.DataFrame,
    config: LabelConfig,
) -> pd.DataFrame:
    """
    Create temporal prediction points efficiently.

    Important optimization:
    entity_type is calculated once per entity instead of
    scanning the complete event dataframe for every point.
    """

    if events.empty:
        raise ValueError(
            "Cannot create prediction points from empty events."
        )

    # ---------------------------------------------------------
    # Validate entity_type consistency once.
    # ---------------------------------------------------------

    entity_type_counts = (
        events.groupby("entity_id")["entity_type"]
        .nunique()
    )

    inconsistent_entities = (
        entity_type_counts[
            entity_type_counts > 1
        ]
        .index
        .tolist()
    )

    if inconsistent_entities:
        raise ValueError(
            "Some entities have multiple entity_type values: "
            + ", ".join(
                map(
                    str,
                    inconsistent_entities[:10],
                )
            )
        )

    # ---------------------------------------------------------
    # Build entity -> entity_type mapping once.
    # ---------------------------------------------------------

    entity_type_map = (
        events[
            [
                "entity_id",
                "entity_type",
            ]
        ]
        .drop_duplicates(
            subset=["entity_id"]
        )
        .set_index("entity_id")[
            "entity_type"
        ]
        .to_dict()
    )

    # ---------------------------------------------------------
    # Maximum timestamp available in dataset.
    # ---------------------------------------------------------

    max_timestamp = events[
        "timestamp"
    ].max()

    rows: list[dict] = []

    # ---------------------------------------------------------
    # Generate prediction points.
    # ---------------------------------------------------------

    for entity_id, group in events.groupby(
        "entity_id",
        sort=False,
    ):
        timestamps = (
            group["timestamp"]
            .drop_duplicates()
            .sort_values()
        )

        entity_type = entity_type_map[
            entity_id
        ]

        for prediction_time in timestamps:

            future_horizon_end = (
                prediction_time
                + pd.Timedelta(
                    days=config.horizon_days
                )
            )

            # We can only create a valid label when the
            # complete future horizon is observable.
            if future_horizon_end > max_timestamp:
                continue

            rows.append(
                {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "prediction_time": prediction_time,
                    "future_horizon_end": future_horizon_end,
                }
            )

    result = pd.DataFrame(
        rows,
        columns=[
            "entity_id",
            "entity_type",
            "prediction_time",
            "future_horizon_end",
        ],
    )

    if result.empty:
        raise ValueError(
            "No valid prediction points were produced. "
            "The dataset needs enough future observation."
        )

    return (
        result
        .sort_values(
            [
                "prediction_time",
                "entity_id",
            ]
        )
        .reset_index(drop=True)
    )


def assign_churn_labels(
    events: pd.DataFrame,
    prediction_points: pd.DataFrame,
    config: LabelConfig,
) -> pd.DataFrame:
    """
    Assign churn labels using only future events for the label.

    This function is optimized by grouping events once per entity.
    """

    if prediction_points.empty:
        raise ValueError(
            "Prediction points are empty."
        )

    # ---------------------------------------------------------
    # Group events once.
    # ---------------------------------------------------------

    grouped_events = {
        entity_id: group[
            [
                "timestamp",
                "event_type",
            ]
        ].sort_values("timestamp")
        for entity_id, group in events.groupby(
            "entity_id",
            sort=False,
        )
    }

    rows: list[dict] = []

    for row in prediction_points.itertuples(
        index=False
    ):
        entity_events = grouped_events[
            row.entity_id
        ]

        future_events = entity_events[
            (entity_events["timestamp"] > row.prediction_time)
            & (
                entity_events["timestamp"]
                <= row.future_horizon_end
            )
        ]

        has_future_activity = (
            not future_events.empty
        )

        rows.append(
            {
                "entity_id": row.entity_id,
                "entity_type": row.entity_type,
                "prediction_time": row.prediction_time,
                "future_horizon_end": row.future_horizon_end,
                "churn_label": int(
                    not has_future_activity
                ),
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:
        raise ValueError(
            "No churn labels were generated."
        )

    return (
        result
        .sort_values(
            [
                "prediction_time",
                "entity_id",
            ]
        )
        .reset_index(drop=True)
    )


def build_labels(
    events: pd.DataFrame,
    config: LabelConfig | None = None,
) -> pd.DataFrame:
    """
    Complete label-generation pipeline.
    """

    config = (
        config
        if config is not None
        else LabelConfig()
    )

    prediction_points = (
        create_prediction_points(
            events,
            config,
        )
    )

    labels = assign_churn_labels(
        events,
        prediction_points,
        config,
    )

    # ---------------------------------------------------------
    # Final label integrity checks.
    # ---------------------------------------------------------

    if labels["churn_label"].isna().any():
        raise ValueError(
            "Generated labels contain null values."
        )

    unique_labels = set(
        labels["churn_label"].unique()
    )

    if not unique_labels.issubset(
        {0, 1}
    ):
        raise ValueError(
            "Churn labels must contain only 0 or 1."
        )

    return labels