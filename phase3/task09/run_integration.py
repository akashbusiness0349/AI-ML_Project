from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path("phase3/task09")


def run_command(
    description: str,
    command: list[str],
) -> None:
    print("\n" + "=" * 70)
    print(description)
    print("=" * 70)

    completed = subprocess.run(
        command,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"{description} failed with exit code "
            f"{completed.returncode}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        required=True,
    )
    parser.add_argument(
        "--source-type",
        required=True,
        choices=["synthetic_demo", "production"],
    )
    args = parser.parse_args()

    python = sys.executable

    run_command(
        "1/6 — DATA VALIDATION",
        [
            python,
            str(ROOT / "run_data_validation.py"),
            "--data",
            args.data,
        ],
    )

    run_command(
        "2/6 — EXPERIMENT + MODEL VARIANTS",
        [
            python,
            str(ROOT / "run_experiment.py"),
            "--data",
            args.data,
            "--source-type",
            args.source_type,
        ],
    )

    run_command(
        "3/6 — PERMANENT HOLDOUT",
        [
            python,
            str(ROOT / "run_holdout.py"),
            "--data",
            args.data,
        ],
    )

    run_command(
        "4/6 — GUARDRAILS",
        [
            python,
            str(ROOT / "run_guardrails.py"),
        ],
    )

    run_command(
        "5/6 — VARIANT SERVING",
        [
            python,
            str(ROOT / "run_variant_serving.py"),
            "--data",
            args.data,
        ],
    )

    run_command(
        "6/6 — INTENTIONAL FAILURE TEST",
        [
            python,
            str(ROOT / "run_failure_test.py"),
        ],
    )

    print("\n" + "=" * 70)
    print("TASK 09 INTEGRATION: PASS")
    print("=" * 70)
    print("Data validation       : PASS")
    print("Model-v1 serving      : PASS")
    print("Model-v2 serving      : PASS")
    print("10% challenger        : CONFIGURED")
    print("10% permanent holdout : CONFIGURED")
    print("Stable assignment     : PASS")
    print("Guardrails            : PASS")
    print("Failure degradation   : PASS")
    print("Model fallback        : PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()