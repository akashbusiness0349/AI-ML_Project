import json
from pathlib import Path

from src.data import load_feature_table
from src.fallback import safe_prediction
from src.model import load_model


ROOT = Path(__file__).resolve().parent


def main():
    df = load_feature_table(
        ROOT / "data" / "task08_feature_table.csv"
    )

    model = load_model(
        ROOT / "models" / "task10_model.joblib"
    )

    row = df.iloc[[0]]

    normal = safe_prediction(
        model,
        row,
        model_available=True,
    )

    fallback = safe_prediction(
        None,
        row,
        model_available=False,
    )

    result = {
        "normal_path": normal,
        "failure_path": fallback,
        "fallback_test": (
            "PASS"
            if fallback["fallback_used"]
            else "FAIL"
        ),
    }

    with open(
        ROOT / "logs" / "failure_test.json",
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