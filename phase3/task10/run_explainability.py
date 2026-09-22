import json
from pathlib import Path

import pandas as pd

from src.data import load_feature_table
from src.model import load_model
from src.explainability import (
    explain_model,
    explain_row,
)


ROOT = Path(__file__).resolve().parent


def main():
    data = load_feature_table(
        ROOT / "data" / "task08_feature_table.csv"
    )

    model = load_model(
        ROOT / "models" / "task10_model.joblib"
    )

    coefficients = explain_model(model)

    row = data.iloc[[0]]

    worked_example = explain_row(
        model,
        row,
    )

    output = {
        "model_explanation": coefficients,
        "worked_example": worked_example,
        "explainability_status": "PASS",
    }

    with open(
        ROOT / "logs" / "explainability.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()