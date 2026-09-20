from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data_ingestion import load_events
from src.features import (
    build_feature_table,
    get_feature_columns,
)
from src.governance import (
    assert_governance_safe,
    build_governance_report,
)
from src.labeling import (
    LabelConfig,
    build_labels,
)
from src.model import (
    MODEL_VERSION,
    save_model,
    train_model,
)
from src.validation import (
    detect_target_leakage,
)


ROOT = Path(__file__).resolve().parent

DEFAULT_DATA = (
    ROOT
    / "data"
    / "demo_events.json"
)

MODEL_PATH = (
    ROOT
    / "models"
    / "churn_model.joblib"
)

LOG_PATH = (
    ROOT
    / "logs"
    / "training.json"
)

FEATURE_LOG_PATH = (
    ROOT
    / "logs"
    / "feature_table.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train Task 08 churn model."
    )

    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA),
        help="Input event JSON.",
    )

    parser.add_argument(
        "--source-type",
        default="synthetic_demo",
        choices=[
            "synthetic_demo",
            "production",
        ],
        help="Data provenance.",
    )

    return parser.parse_args()


def chronological_split(
    dataframe,
):
    dataframe = dataframe.sort_values(
        "prediction_time"
    ).reset_index(
        drop=True
    )

    n = len(dataframe)

    train_end = int(
        n * 0.60
    )

    validation_end = int(
        n * 0.80
    )

    train = dataframe.iloc[
        :train_end
    ].copy()

    validation = dataframe.iloc[
        train_end:validation_end
    ].copy()

    holdout = dataframe.iloc[
        validation_end:
    ].copy()

    if train.empty:
        raise ValueError(
            "Training split is empty."
        )

    if validation.empty:
        raise ValueError(
            "Validation split is empty."
        )

    if holdout.empty:
        raise ValueError(
            "Held-out split is empty."
        )

    return (
        train,
        validation,
        holdout,
    )


def main() -> None:
    args = parse_args()

    data_path = Path(
        args.data
    )

    print("=" * 72)
    print("PHASE 3 / TASK 08 — CHURN MODEL TRAINING")
    print("=" * 72)

    print(
        f"Data source           : {args.source_type}"
    )

    events = load_events(
        data_path
    )

    label_config = LabelConfig(
        lookback_days=14,
        horizon_days=14,
    )

    labels = build_labels(
        events,
        config=label_config,
    )

    feature_table = build_feature_table(
        events,
        labels,
        config=label_config,
    )

    feature_columns = get_feature_columns()

    leakage = detect_target_leakage(
        feature_columns
    )

    if leakage:
        raise ValueError(
            "Potential target leakage detected: "
            + ", ".join(leakage)
        )

    assert_governance_safe(
        raw_columns=events.columns.tolist(),
        feature_columns=feature_columns,
    )

    (
        train,
        validation,
        holdout,
    ) = chronological_split(
        feature_table
    )

    if train["churn_label"].nunique() < 2:
        raise ValueError(
            "Training split contains only one class. "
            "More temporal data is required."
        )

    model = train_model(
        train,
        feature_columns,
    )

    metadata = {
        "model_version": MODEL_VERSION,
        "data_source_type": args.source_type,
        "data_path": str(data_path),
        "label_definition": (
            "churn=1 when no qualifying activity occurs "
            "during the complete future 14-day horizon."
        ),
        "lookback_days": 14,
        "horizon_days": 14,
        "split": {
            "train_fraction": 0.60,
            "validation_fraction": 0.20,
            "holdout_fraction": 0.20,
            "method": "chronological",
        },
        "feature_columns": feature_columns,
        "event_rows": len(events),
        "labeled_rows": len(feature_table),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "holdout_rows": len(holdout),
        "train_churn_rate": float(
            train["churn_label"].mean()
        ),
        "validation_churn_rate": float(
            validation["churn_label"].mean()
        ),
        "holdout_churn_rate": float(
            holdout["churn_label"].mean()
        ),
    }

    save_model(
        model,
        MODEL_PATH,
        feature_columns,
        metadata=metadata,
    )

    FEATURE_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_table.to_csv(
        FEATURE_LOG_PATH,
        index=False,
    )

    governance = build_governance_report(
        raw_columns=events.columns.tolist(),
        feature_columns=feature_columns,
    )

    training_log = {
        "status": "success",
        "metadata": metadata,
        "governance": governance,
        "production_data_note": (
            "Synthetic demo data is not production evidence."
            if args.source_type
            == "synthetic_demo"
            else (
                "Metrics are based on the supplied production "
                "dataset."
            )
        ),
    }

    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            training_log,
            handle,
            indent=2,
            default=str,
        )

    print()
    print(
        f"Events                : {len(events)}"
    )

    print(
        f"Labeled rows          : "
        f"{len(feature_table)}"
    )

    print(
        f"Train rows            : "
        f"{len(train)}"
    )

    print(
        f"Validation rows       : "
        f"{len(validation)}"
    )

    print(
        f"Holdout rows          : "
        f"{len(holdout)}"
    )

    print(
        f"Train churn rate      : "
        f"{train['churn_label'].mean():.4f}"
    )

    print(
        f"Validation churn rate : "
        f"{validation['churn_label'].mean():.4f}"
    )

    print(
        f"Holdout churn rate    : "
        f"{holdout['churn_label'].mean():.4f}"
    )

    print()
    print(
        f"Model                 : {MODEL_VERSION}"
    )

    print(
        f"Model artifact        : {MODEL_PATH}"
    )

    print(
        f"Training evidence     : {LOG_PATH}"
    )

    print()
    print("TRAINING: PASS")


if __name__ == "__main__":
    main()