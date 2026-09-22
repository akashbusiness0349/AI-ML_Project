from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = [
    "entity_id",
    "prediction_time",
    "future_horizon_end",
    "churn_label",
    "event_count_14d",
    "active_days_14d",
    "days_since_last_activity",
    "event_type_diversity_14d",
    "recent_3d_events",
    "recent_7d_events",
    "activity_rate_14d",
]


FEATURE_COLUMNS = [
    "event_count_14d",
    "active_days_14d",
    "days_since_last_activity",
    "event_type_diversity_14d",
    "recent_3d_events",
    "recent_7d_events",
    "activity_rate_14d",
]


TARGET_COLUMN = "churn_label"


def load_feature_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["prediction_time"] = pd.to_datetime(
        df["prediction_time"], utc=True, errors="coerce"
    )
    df["future_horizon_end"] = pd.to_datetime(
        df["future_horizon_end"], utc=True, errors="coerce"
    )

    if df["prediction_time"].isna().any():
        raise ValueError("Invalid prediction_time values found.")

    if df["future_horizon_end"].isna().any():
        raise ValueError("Invalid future_horizon_end values found.")

    df = df.sort_values(
        ["prediction_time", "entity_id"]
    ).reset_index(drop=True)

    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)

    if not set(df[TARGET_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("Target must be binary 0/1.")

    return df


def validate_no_target_leakage(df: pd.DataFrame) -> dict:
    forbidden = {
        TARGET_COLUMN,
        "future_horizon_end",
        "future_activity",
        "future_events",
        "outcome",
        "label",
    }

    leakage = []

    for feature in FEATURE_COLUMNS:
        lower = feature.lower()

        if (
            lower in forbidden
            or "future" in lower
            or "outcome" in lower
            or "label" in lower
        ):
            leakage.append(feature)

    if leakage:
        raise ValueError(f"Target leakage detected: {leakage}")

    return {
        "status": "PASS",
        "target": TARGET_COLUMN,
        "features": FEATURE_COLUMNS,
        "future_columns_excluded": True,
        "leakage_features": [],
    }


def chronological_split(
    df: pd.DataFrame,
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
):
    n = len(df)

    train_end = int(n * train_fraction)
    validation_end = int(
        n * (train_fraction + validation_fraction)
    )

    train = df.iloc[:train_end].copy()
    validation = df.iloc[train_end:validation_end].copy()
    holdout = df.iloc[validation_end:].copy()

    return train, validation, holdout