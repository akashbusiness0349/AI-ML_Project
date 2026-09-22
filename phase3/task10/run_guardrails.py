import json
from pathlib import Path

from src.guardrails import evaluate_guardrails


ROOT = Path(__file__).resolve().parent


def main():
    with open(
        ROOT / "logs" / "experiment_result.json",
        encoding="utf-8",
    ) as f:
        experiment = json.load(f)

    with open(
        ROOT / "logs" / "preregistration.json",
        encoding="utf-8",
    ) as f:
        prereg = json.load(f)

    result = evaluate_guardrails(
        {
            "ab_effect": experiment[
                "offline_ab_replay"
            ]
        },
        prereg,
    )

    with open(
        ROOT / "logs" / "guardrail_result.json",
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