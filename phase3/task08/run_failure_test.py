from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.fallback import (
    fallback_predictions,
    model_unavailable_response,
)


ROOT = Path(__file__).resolve().parent

FEATURE_PATH = (
    ROOT
    / "logs"
    / "feature_table.csv"
)

OUTPUT_PATH = (
    ROOT
    / "logs"
    / "failure_test.json"
)

FALLBACK_PATH = (
    ROOT
    / "logs"
    / "fallback_predictions.csv"
)


def main() -> None:
    print("=" * 72)
    print(
        "PHASE 3 / TASK 08 — FAILURE PATH TEST"
    )
    print("=" * 72)

    features = pd.read_csv(
        FEATURE_PATH,
        parse_dates=[
            "prediction_time",
            "future_horizon_end",
        ],
    )

    response = model_unavailable_response(
        reason="INTENTIONAL_FAILURE_TEST"
    )

    fallback = fallback_predictions(
        features
    )

    fallback_rows = fallback[
        [
            "entity_id",
            "entity_type",
            "prediction_time",
            "churn_probability",
            "prediction_source",
            "model_prediction",
        ]
    ].head(20)

    fallback_rows.to_csv(
        FALLBACK_PATH,
        index=False,
    )

    result = {
        "failure_injected": True,
        "model_status": response[
            "status"
        ],
        "fallback_source": response[
            "prediction_source"
        ],
        "fallback_rows_generated": len(
            fallback
        ),
        "designed_behavior": (
            "Use deterministic recency-based "
            "risk when ML model is unavailable."
        ),
        "system_crash": False,
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            result,
            handle,
            indent=2,
        )

    print()
    print(
        "Failure injected     : YES"
    )

    print(
        f"Model status         : "
        f"{response['status']}"
    )

    print(
        f"Fallback rows        : "
        f"{len(fallback)}"
    )

    print(
        "Designed degradation : "
        "NON_ML_FALLBACK"
    )

    print(
        f"Fallback evidence    : "
        f"{FALLBACK_PATH}"
    )

    print(
        f"Failure evidence     : "
        f"{OUTPUT_PATH}"
    )

    print()
    print(
        "FAILURE PATH TEST: PASS"
    )


if __name__ == "__main__":
    main()