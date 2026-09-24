from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


SCRIPTS = [
    "run_data_validation.py",
    "run_position_bias.py",
    "run_training.py",
    "run_evaluation.py",
    "run_explainability.py",
    "run_failure_test.py",
    "run_demo.py",
]


def run_script(script: str) -> None:
    print("\n" + "=" * 80)
    print(f"RUNNING: {script}")
    print("=" * 80)

    result = subprocess.run(
        [
            sys.executable,
            script,
        ],
        cwd=BASE_DIR,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FAILED: {script}"
        )


def load_json(path: str) -> dict:
    with open(
        BASE_DIR / path,
        encoding="utf-8",
    ) as f:
        return json.load(f)


def main() -> None:
    for script in SCRIPTS:
        run_script(script)

    validation = load_json(
        "logs/data_validation.json"
    )

    bias = load_json(
        "logs/position_bias.json"
    )

    training = load_json(
        "logs/training_result.json"
    )

    evaluation = load_json(
        "logs/evaluation_result.json"
    )

    explainability = load_json(
        "logs/explainability.json"
    )

    failure = load_json(
        "logs/failure_test.json"
    )

    demo = load_json(
        "logs/live_demo.json"
    )

    delta = evaluation[
        "metrics"
    ]["delta"]

    ltr_ndcg5 = evaluation[
        "metrics"
    ]["ltr"]["nDCG@5"]

    baseline_ndcg5 = evaluation[
        "metrics"
    ]["baseline"]["nDCG@5"]

    decision = (
        "READY_FOR_ONLINE_TEST"
        if (
            ltr_ndcg5
            > baseline_ndcg5
            and failure["status"] == "PASS"
            and explainability["status"] == "PASS"
        )
        else "OFFLINE_EVALUATION_COMPLETE"
    )

    summary = {
        "task": "Phase 3 Task 11",
        "status": "COMPLETED",
        "dataset": {
            "source_type": (
                "synthetic_logged_impressions"
            ),
            "production_evidence_status": (
                "NOT_PRODUCTION_EVIDENCE"
            ),
        },
        "data_validation": validation[
            "status"
        ],
        "position_bias": bias[
            "status"
        ],
        "ltr_training": training[
            "status"
        ],
        "offline_evaluation": evaluation[
            "status"
        ],
        "explainability": explainability[
            "status"
        ],
        "failure_test": failure[
            "status"
        ],
        "executable_demo": demo[
            "status"
        ],
        "nDCG@5": {
            "ltr": ltr_ndcg5,
            "baseline": baseline_ndcg5,
            "delta": delta[
                "nDCG@5"
            ],
        },
        "MAP": {
            "ltr": evaluation[
                "metrics"
            ]["ltr"]["MAP"],
            "baseline": evaluation[
                "metrics"
            ]["baseline"]["MAP"],
            "delta": delta["MAP"],
        },
        "online_validation": {
            "status": "NOT_ESTABLISHED",
            "reason": (
                "Offline evidence does not establish "
                "online causal impact."
            ),
        },
        "final_status": decision,
    }

    with open(
        BASE_DIR
        / "logs"
        / "integration_summary.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print("TASK 11 INTEGRATION COMPLETE")
    print("=" * 80)
    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()