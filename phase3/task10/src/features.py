import numpy as np
import pandas as pd


FEATURES = [
    "event_count_1d",
    "event_count_7d",
    "event_count_14d",
    "days_since_last_event",
    "activity_velocity",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Leakage-safe temporal feature construction.

    Every feature for an event uses only events that occurred
    before that event for the same entity.
    """
    working = (
        df.copy()
        .sort_values(
            ["entity_id", "event_timestamp"]
        )
    )

    rows = []

    for entity_id, group in working.groupby(
        "entity_id",
        sort=False,
    ):
        group = group.reset_index(drop=True)

        for index in range(len(group)):
            current = group.iloc[index]
            previous = group.iloc[:index]

            timestamp = current["event_timestamp"]

            count_1d = int(
                (
                    previous["event_timestamp"]
                    >= timestamp - pd.Timedelta(days=1)
                ).sum()
            )

            count_7d = int(
                (
                    previous["event_timestamp"]
                    >= timestamp - pd.Timedelta(days=7)
                ).sum()
            )

            count_14d = int(
                (
                    previous["event_timestamp"]
                    >= timestamp - pd.Timedelta(days=14)
                ).sum()
            )

            if len(previous) > 0:
                last_timestamp = previous[
                    "event_timestamp"
                ].iloc[-1]

                days_since = max(
                    (
                        timestamp - last_timestamp
                    ).total_seconds() / 86400.0,
                    0.0,
                )

                previous_label = float(
                    previous["outcome_label"].iloc[-1]
                )

                velocity = (
                    float(current["outcome_label"])
                    - previous_label
                ) / max(days_since, 1 / 24)

            else:
                days_since = 14.0
                velocity = 0.0

            record = current.to_dict()

            record.update(
                {
                    "event_count_1d": count_1d,
                    "event_count_7d": count_7d,
                    "event_count_14d": count_14d,
                    "days_since_last_event": days_since,
                    "activity_velocity": velocity,
                }
            )

            rows.append(record)

    result = pd.DataFrame(rows)

    result[FEATURES] = (
        result[FEATURES]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )

    return result