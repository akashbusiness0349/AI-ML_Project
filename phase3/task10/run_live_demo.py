import json
from pathlib import Path

from src.data import load_feature_table
from src.fallback import safe_prediction
from src.model import load_model
from src.experiment import assign_variant


ROOT = Path(__file__).resolve().parent


def main():
    df = load_feature_table(
        ROOT / "data" / "task08_feature_table.csv"
    )

    model = load_model(
        ROOT / "models" / "task10_model.joblib"
    )

    samples = df.head(5)

    rows = []

    for _, row in samples.iterrows():
        one = row.to_frame().T

        variant = assign_variant(
            row["entity_id"]
        )

        if variant == "treatment":
            result = safe_prediction(
                model,
                one,
                model_available=True,
            )
        else:
            result = safe_prediction(
                None,
                one,
                model_available=False,
            )

        rows.append(
            {
                "entity_id": row["entity_id"],
                "assigned_variant": variant,
                **result,
            }
        )

    output = {
        "demo_type": "executable_offline_ab_replay",
        "data_source": "task08_feature_table.csv",
        "production_status": "NOT_LIVE_PRODUCTION",
        "records_served": rows,
        "fallback_supported": True,
    }

    with open(
        ROOT / "logs" / "live_demo.json",
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