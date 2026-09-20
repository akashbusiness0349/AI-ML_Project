from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

DEFAULT_DATA = (
    ROOT
    / "data"
    / "demo_events.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run complete Task 08 pipeline."
        )
    )

    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA),
        help=(
            "Event JSON path. Defaults to "
            "synthetic demo data."
        ),
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


def run_step(
    script_name: str,
    extra_args: list[str] | None = None,
) -> None:
    print()
    print("=" * 72)
    print(
        f"RUNNING: {script_name}"
    )
    print("=" * 72)

    command = [
        sys.executable,
        str(
            ROOT / script_name
        ),
    ]

    if extra_args:
        command.extend(
            extra_args
        )

    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"\nIntegration failed at "
            f"{script_name} "
            f"with exit code "
            f"{result.returncode}."
        )


def main() -> None:
    args = parse_args()

    print("=" * 72)
    print(
        "PHASE 3 / TASK 08 — "
        "END-TO-END INTEGRATION"
    )
    print("=" * 72)

    print()
    print(
        f"Data source           : "
        f"{args.source_type}"
    )

    print(
        f"Data file             : "
        f"{args.data}"
    )

    run_step(
        "run_data_validation.py",
        [
            "--data",
            args.data,
            "--source-type",
            args.source_type,
        ],
    )

    run_step(
        "run_training.py",
        [
            "--data",
            args.data,
            "--source-type",
            args.source_type,
        ],
    )

    run_step(
        "run_evaluation.py",
        [
            "--source-type",
            args.source_type,
        ],
    )

    run_step(
        "run_demo.py",
        [
            "--source-type",
            args.source_type,
        ],
    )

    run_step(
        "run_failure_test.py"
    )

    print()
    print("=" * 72)
    print(
        "TASK 08 INTEGRATION: PASS"
    )
    print("=" * 72)

    print()
    print(
        "Generated evidence:"
    )

    print(
        "  logs/data_validation.json"
    )

    print(
        "  logs/training.json"
    )

    print(
        "  logs/feature_table.csv"
    )

    print(
        "  logs/evaluation.json"
    )

    print(
        "  logs/precision_recall_curve.png"
    )

    print(
        "  logs/operating_threshold.json"
    )

    print(
        "  logs/at_risk_users.csv"
    )

    print(
        "  logs/demo_output.json"
    )

    print(
        "  logs/failure_test.json"
    )

    print(
        "  logs/fallback_predictions.csv"
    )

    print(
        "  models/churn_model.joblib"
    )


if __name__ == "__main__":
    main()