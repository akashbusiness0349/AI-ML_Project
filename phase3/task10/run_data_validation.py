import json
from pathlib import Path

from src.data import (
    load_feature_table,
    validate_no_target_leakage,
    FEATURE_COLUMNS,
)


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "task08_feature_table.csv"
LOGS = ROOT / "logs"


def main():
    df = load_feature_table(DATA)
    leakage = validate_no_target_leakage(df)

    result = {
        "status": "PASS",
        "rows": len(df),
        "entities": int(
            df["entity_id"].nunique()
        ),
        "first_prediction_time": str(
            df["prediction_time"].min()
        ),
        "last_prediction_time": str(
            df["prediction_time"].max()
        ),
        "target": "churn_label",
        "target_distribution": {
            str(k): int(v)
            for k, v in df["churn_label"]
            .value_counts()
            .items()
        },
        "features": FEATURE_COLUMNS,
        "leakage_audit": leakage,
        "source_type": "synthetic_demo",
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
    }

    LOGS.mkdir(exist_ok=True)

    with open(
        LOGS / "data_validation.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()